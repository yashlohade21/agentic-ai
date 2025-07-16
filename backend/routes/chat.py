import logging
import asyncio
from flask import Blueprint, jsonify, request, session
from datetime import datetime
from database import get_db  # Assuming you have this helper
from routes.models import ChatMessage  # Assuming you have this model
from main import BinarybrainedSystem  # Import your actual AI system
from routes.auth import require_auth

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create a Blueprint for chat routes
chat_bp = Blueprint('chat', __name__)

class AIChatSystem:
    """
    A wrapper class to manage the BinarybrainedSystem within a Flask application.
    It handles the async nature of the core AI system.
    """
    def __init__(self):
        self.ai_system = BinarybrainedSystem()
        self.initialized = False
        # Run the async initialization method in a blocking way upon startup.
        try:
            logging.info("Attempting to initialize AI system...")
            # This creates a new event loop to run the async initialize function.
            asyncio.run(self.initialize())
        except Exception as e:
            logging.error(f"Fatal error during initial construction: {e}", exc_info=True)

    async def initialize(self):
        """
        Asynchronously initializes the core AI system.
        """
        try:
            # The `initialize` method in BinarybrainedSystem is async
            await self.ai_system.initialize()
            self.initialized = True
            logging.info("AI system initialized successfully.")
        except Exception as e:
            self.initialized = False
            logging.error(f"AI system initialization failed: {e}", exc_info=True)

    def process_message(self, message: str, user_id: int) -> dict:
        """
        Processes a user message by calling the async AI system and handles DB operations.
        """
        if not self.initialized:
            logging.warning("Process message called but system is not initialized.")
            return {"success": False, "error": "AI system is not ready. Please try again later."}

        try:
            # Run the async `process_request` method from the synchronous Flask route.
            # asyncio.run() creates a new event loop for this single task.
            logging.info(f"Processing message for user_id: {user_id}")
            ai_result = asyncio.run(self.ai_system.process_request(message))
            
            ai_response_content = ai_result.get("response", "I could not generate a response.")
            metadata = ai_result.get("metadata", {})

            # --- Database Operations ---
            db = None
            try:
                db = next(get_db())
                
                # Save user message to DB
                user_msg = ChatMessage(
                    content=message,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    sender='user' # Assuming your model has a sender field
                )
                db.add(user_msg)
                
                # Save AI response to DB
                ai_msg = ChatMessage(
                    content=ai_response_content,
                    timestamp=datetime.now(),
                    user_id=user_id, # Link AI message to the user's session
                    sender='bot' # Assuming your model has a sender field
                )
                db.add(ai_msg)
                
                db.commit()
                logging.info(f"Successfully saved chat for user_id: {user_id}")
                
            except Exception as db_error:
                logging.error(f"Database error for user_id {user_id}: {db_error}", exc_info=True)
                if db:
                    db.rollback()
                # Even if DB fails, we should still return the response to the user.
                metadata['db_error'] = f"Failed to save message history: {db_error}"
            finally:
                if db:
                    db.close()
            # --- End of Database Operations ---

            return {
                "success": True,
                "response": ai_response_content,
                "metadata": metadata
            }
                
        except Exception as e:
            # This will catch errors from `process_request` or other logic.
            logging.error(f"Error in process_message for user_id {user_id}: {e}", exc_info=True)
            return {
                "success": False,
                "error": "An unexpected error occurred while processing your message."
            }

# Create a single, shared instance of the AIChatSystem.
# This ensures the AI model is loaded only once when the app starts.
ai_chat = AIChatSystem()

@chat_bp.route('/chat/status', methods=['GET'])
def get_status():
    """Endpoint to get the current status of the AI system."""
    try:
        status_data = {
            'status': 'active' if ai_chat.initialized else 'initializing_failed',
            'agents': ['enhanced_orchestrator', 'enhanced_coder', 'researcher'], # This can be dynamic later
            'session_requests': 0  # Placeholder for session tracking
        }
        return jsonify(status_data), 200
    except Exception as e:
        logging.error(f"Error in /chat/status endpoint: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve system status'}), 500
    
@chat_bp.route("/chat", methods=["POST"])
@require_auth
def chat():
    """Main endpoint to handle incoming chat messages."""

    logging.info(f"Session at /chat: {session}")
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Invalid request body, "message" field is missing'}), 400
        
    message = data['message'].strip()
    if not message:
        return jsonify({'error': 'Message content cannot be empty'}), 400
        
    user_id = session['user_id']
    
    try:
        result = ai_chat.process_message(message=message, user_id=user_id)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'response': result['response'],
                'metadata': result.get('metadata', {})
            }), 200
        else:
            # Send a specific error from our system if available
            error_message = result.get('error', 'Processing failed due to an unknown error.')
            return jsonify({'error': error_message}), 500
            
    except Exception as e:
        # This is a final catch-all for any unexpected errors in the endpoint itself.
        logging.error(f"Critical error in /chat endpoint for user_id {user_id}: {e}", exc_info=True)
        return jsonify({'error': 'A critical internal server error occurred.'}), 500

