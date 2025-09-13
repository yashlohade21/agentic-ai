from flask import Blueprint, request, jsonify, session
from firebase_config import get_firestore_client
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

chats_bp = Blueprint('chats', __name__)

def get_db():
    """Get Firestore client"""
    return get_firestore_client()

@chats_bp.route('/api/chats/user/<user_id>', methods=['GET'])
def get_user_chats(user_id):
    """Get all chats for a user"""
    try:
        logger.info(f"Fetching chats for user: {user_id}")
        db = get_db()
        if not db:
            logger.warning("Database not available")
            return jsonify({'chats': []})
        
        # Get chats for the user, ordered by last update
        chats_ref = db.collection('chats')
        query = chats_ref.where('userId', '==', user_id).order_by('lastUpdated', direction='DESCENDING')
        
        chats = []
        try:
            docs = query.stream()
            for doc in docs:
                chat_data = doc.to_dict()
                chat_data['id'] = doc.id
                
                # Add preview from last message
                if 'messages' in chat_data and chat_data['messages']:
                    last_message = chat_data['messages'][-1]
                    chat_data['preview'] = last_message.get('content', '')[:100]
                
                # Remove full messages from list view
                chat_data.pop('messages', None)
                chats.append(chat_data)
            
            logger.info(f"Found {len(chats)} chats for user {user_id}")
        except Exception as query_error:
            logger.error(f"Query error: {query_error}")
            # Try without ordering if the index doesn't exist
            try:
                simple_query = chats_ref.where('userId', '==', user_id)
                for doc in simple_query.stream():
                    chat_data = doc.to_dict()
                    chat_data['id'] = doc.id
                    
                    # Add preview from last message
                    if 'messages' in chat_data and chat_data['messages']:
                        last_message = chat_data['messages'][-1]
                        chat_data['preview'] = last_message.get('content', '')[:100]
                    
                    # Remove full messages from list view
                    chat_data.pop('messages', None)
                    chats.append(chat_data)
                
                # Sort by lastUpdated in Python if we can't do it in the query
                chats.sort(key=lambda x: x.get('lastUpdated', ''), reverse=True)
                logger.info(f"Found {len(chats)} chats using simple query")
            except Exception as fallback_error:
                logger.error(f"Fallback query also failed: {fallback_error}")
        
        return jsonify({'chats': chats})
    except Exception as e:
        logger.error(f"Error fetching user chats: {e}")
        return jsonify({'chats': []})

@chats_bp.route('/api/chats/<chat_id>', methods=['GET'])
def get_chat(chat_id):
    """Get a specific chat with all messages"""
    try:
        db = get_db()
        if not db:
            return jsonify({'error': 'Database not available'}), 503
        
        chat_ref = db.collection('chats').document(chat_id)
        chat_doc = chat_ref.get()
        
        if not chat_doc.exists:
            return jsonify({'error': 'Chat not found'}), 404
        
        chat_data = chat_doc.to_dict()
        chat_data['id'] = chat_doc.id
        
        return jsonify(chat_data)
    except Exception as e:
        logger.error(f"Error fetching chat: {e}")
        return jsonify({'error': 'Failed to fetch chat'}), 500

@chats_bp.route('/api/chats', methods=['POST'])
def create_chat():
    """Create a new chat"""
    try:
        data = request.get_json()
        user_id = data.get('userId')
        title = data.get('title', 'New Chat')
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        db = get_db()
        if not db:
            return jsonify({'error': 'Database not available'}), 503
        
        # Create new chat document
        chat_id = str(uuid.uuid4())
        chat_data = {
            'userId': user_id,
            'title': title,
            'messages': [],
            'createdAt': datetime.utcnow().isoformat(),
            'lastUpdated': datetime.utcnow().isoformat()
        }
        
        db.collection('chats').document(chat_id).set(chat_data)
        
        chat_data['id'] = chat_id
        return jsonify(chat_data), 201
    except Exception as e:
        logger.error(f"Error creating chat: {e}")
        return jsonify({'error': 'Failed to create chat'}), 500

@chats_bp.route('/api/chats/<chat_id>', methods=['PUT'])
def update_chat(chat_id):
    """Update chat messages"""
    try:
        data = request.get_json()
        messages = data.get('messages', [])
        
        db = get_db()
        if not db:
            return jsonify({'error': 'Database not available'}), 503
        
        chat_ref = db.collection('chats').document(chat_id)
        
        # Update chat with new messages
        chat_ref.update({
            'messages': messages,
            'lastUpdated': datetime.utcnow().isoformat()
        })
        
        # Auto-generate title from first message if not set
        if messages and len(messages) == 1:
            first_message = messages[0].get('content', '')
            title = first_message[:50] + ('...' if len(first_message) > 50 else '')
            chat_ref.update({'title': title})
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error updating chat: {e}")
        return jsonify({'error': 'Failed to update chat'}), 500

@chats_bp.route('/api/chats/<chat_id>/title', methods=['PATCH'])
def update_chat_title(chat_id):
    """Update chat title"""
    try:
        data = request.get_json()
        title = data.get('title')
        
        if not title:
            return jsonify({'error': 'Title required'}), 400
        
        db = get_db()
        if not db:
            return jsonify({'error': 'Database not available'}), 503
        
        chat_ref = db.collection('chats').document(chat_id)
        chat_ref.update({
            'title': title,
            'lastUpdated': datetime.utcnow().isoformat()
        })
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error updating chat title: {e}")
        return jsonify({'error': 'Failed to update chat title'}), 500

@chats_bp.route('/api/chats/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    """Delete a chat"""
    try:
        db = get_db()
        if not db:
            return jsonify({'error': 'Database not available'}), 503
        
        db.collection('chats').document(chat_id).delete()
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error deleting chat: {e}")
        return jsonify({'error': 'Failed to delete chat'}), 500