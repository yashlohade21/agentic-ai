import logging
import asyncio
import os
from flask import Blueprint, jsonify, request, session
from datetime import datetime

# Configure logging first
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from firebase_config import db
except:
    from firebase_config_mock import db

# Import auth requirement
from routes.auth import require_auth

# Import the LLM manager
try:
    from core.llm_manager_fixed import create_llm_manager
    from core.config import settings
    logger.info(f"LLM Manager imported successfully. API keys present: BINARYBRAINED={bool(settings.binarybrained_api_key)}, MISTRAL={bool(settings.mistral_api_key)}")
except Exception as e:
    logger.error(f"Failed to import LLM manager: {e}")
    raise

# BinarybrainedSystem using the LLM manager
class BinarybrainedSystem:
    def __init__(self):
        self.llm_manager = None
        self.system_prompt = """You are a helpful AI assistant. Provide clear, accurate, and helpful responses to user questions.
        Be conversational, friendly, and professional. If you're unsure about something, say so honestly."""

    async def initialize(self):
        """Initialize the LLM manager with configured providers"""
        try:
            self.llm_manager = create_llm_manager(settings)
            logger.info(f"LLM manager initialized with providers: {[p.name for p in self.llm_manager.providers]}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM manager: {e}", exc_info=True)
            raise

    async def process_request(self, message):
        """Process user message using the LLM manager"""
        try:
            if not self.llm_manager:
                await self.initialize()

            # Generate response using LLM manager
            response = await self.llm_manager.generate(
                prompt=message,
                system_prompt=self.system_prompt
            )

            # Get provider status for metadata
            status = self.llm_manager.get_status()

            return {
                "response": response,
                "metadata": {
                    "status": "active",
                    "provider_status": status
                }
            }
        except Exception as e:
            logger.error(f"Error processing request with message '{message[:50]}...': {e}", exc_info=True)
            # Fallback response
            return {
                "response": "I apologize, but I'm having trouble processing your request. Please try again or check the system configuration.",
                "metadata": {"status": "error", "error": str(e)}
            }

# Create a Blueprint for chat routes
chat_bp = Blueprint("chat", __name__)

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
            logger.info("Attempting to initialize AI system...")
            # This creates a new event loop to run the async initialize function.
            asyncio.run(self.initialize())
        except Exception as e:
            logger.error(f"Fatal error during initial construction: {e}", exc_info=True)

    async def initialize(self):
        """
        Asynchronously initializes the core AI system.
        """
        try:
            # The `initialize` method in BinarybrainedSystem is async
            await self.ai_system.initialize()
            self.initialized = True
            logger.info("AI system initialized successfully.")
        except Exception as e:
            self.initialized = False
            logger.error(f"AI system initialization failed: {e}", exc_info=True)

    def process_message(self, message: str, user_id: str) -> dict:
        """
        Processes a user message by calling the async AI system and handles DB operations.
        """
        if not self.initialized:
            logger.warning("Process message called but system is not initialized.")
            return {"success": False, "error": "AI system is not ready. Please try again later."}

        try:
            # Run the async `process_request` method from the synchronous Flask route.
            # asyncio.run() creates a new event loop for this single task.
            logger.info(f"Processing message for user_id: {user_id}")
            ai_result = asyncio.run(self.ai_system.process_request(message))
            
            ai_response_content = ai_result.get("response", "I could not generate a response.")
            metadata = ai_result.get("metadata", {})

            # --- Database Operations ---
            try:
                chat_messages_ref = db.collection("chat_messages")
                
                # Save user message to DB
                chat_messages_ref.add({
                    "content": message,
                    "timestamp": datetime.now(),
                    "user_id": user_id,
                    "sender": "user"
                })
                
                # Save AI response to DB
                chat_messages_ref.add({
                    "content": ai_response_content,
                    "timestamp": datetime.now(),
                    "user_id": user_id,
                    "sender": "bot"
                })
                
                logger.info(f"Successfully saved chat for user_id: {user_id}")

            except Exception as db_error:
                logger.error(f"Database error for user_id {user_id}: {db_error}", exc_info=True)
                # Even if DB fails, we should still return the response to the user.
                metadata["db_error"] = f"Failed to save message history: {db_error}"
            # --- End of Database Operations ---

            return {
                "success": True,
                "response": ai_response_content,
                "metadata": metadata
            }
                
        except Exception as e:
            # This will catch errors from `process_request` or other logic.
            logger.error(f"Error in process_message for user_id {user_id}: {e}", exc_info=True)
            return {
                "success": False,
                "error": "An unexpected error occurred while processing your message."
            }

# Create a single, shared instance of the AIChatSystem.
# This ensures the AI model is loaded only once when the app starts.
ai_chat = AIChatSystem()

@chat_bp.route("/chat/status", methods=["GET"])
def get_status():
    """Endpoint to get the current status of the AI system."""
    try:
        # Include detailed debugging info
        debug_info = {
            "initialized": ai_chat.initialized,
            "llm_manager_exists": ai_chat.ai_system.llm_manager is not None if ai_chat.ai_system else False,
            "env_vars": {
                "BINARYBRAINED_API_KEY": bool(os.getenv('BINARYBRAINED_API_KEY')),
                "MISTRAL_API_KEY": bool(os.getenv('MISTRAL_API_KEY')),
                "OPENAI_API_KEY": bool(os.getenv('OPENAI_API_KEY')),
            },
            "config_api_keys": {
                "binarybrained": bool(settings.binarybrained_api_key) if 'settings' in globals() else False,
                "mistral": bool(settings.mistral_api_key) if 'settings' in globals() else False,
            }
        }

        # Try to get LLM manager status if available
        if ai_chat.initialized and ai_chat.ai_system and ai_chat.ai_system.llm_manager:
            try:
                debug_info["llm_status"] = ai_chat.ai_system.llm_manager.get_status()
            except:
                debug_info["llm_status"] = "Error getting LLM status"

        status_data = {
            "status": "active" if ai_chat.initialized else "initializing_failed",
            "agents": ["enhanced_orchestrator", "enhanced_coder", "researcher"],
            "session_requests": 0,
            "debug": debug_info
        }
        return jsonify(status_data), 200
    except Exception as e:
        logger.error(f"Error in /chat/status endpoint: {e}", exc_info=True)
        return jsonify({"error": f"Failed to retrieve system status: {str(e)}"}), 500
    
@chat_bp.route("/chat", methods=["POST"])
@require_auth
def chat():
    """Main endpoint to handle incoming chat messages."""

    logger.info(f"Session at /chat: {session}")
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Invalid request body, \"message\" field is missing"}), 400
        
    message = data["message"].strip()
    if not message:
        return jsonify({"error": "Message content cannot be empty"}), 400
        
    user_id = session["user_id"]
    
    try:
        result = ai_chat.process_message(message=message, user_id=user_id)
        
        if result.get("success"):
            return jsonify({
                "success": True,
                "response": result["response"],
                "metadata": result.get("metadata", {})
            }), 200
        else:
            # Send a specific error from our system if available
            error_message = result.get("error", "Processing failed due to an unknown error.")
            return jsonify({"error": error_message}), 500
            
    except Exception as e:
        # This is a final catch-all for any unexpected errors in the endpoint itself.
        logger.error(f"Critical error in /chat endpoint for user_id {user_id}: {e}", exc_info=True)
        return jsonify({"error": "A critical internal server error occurred."}) , 500


