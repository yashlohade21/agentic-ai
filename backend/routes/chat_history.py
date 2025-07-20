import logging
from flask import Blueprint, jsonify, request, session
from datetime import datetime, timedelta
try:
    from firebase_config import db
except:
    from firebase_config_mock import db
from routes.auth import require_auth

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint for chat history routes
chat_history_bp = Blueprint("chat_history", __name__)

@chat_history_bp.route('/history', methods=['GET'])
@require_auth
def get_chat_history():
    """Get chat history for the current user"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        days = request.args.get('days', 7, type=int)  # Default to last 7 days
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        logger.info(f"Fetching chat history for user {user_id}, limit: {limit}, offset: {offset}")
        
        # Query chat messages from database
        chat_messages_ref = db.collection("chat_messages")
        
        # For mock database, we'll simulate the query
        if hasattr(db, 'data'):  # Mock database
            all_messages = []
            chat_data = db.data.get("chat_messages", {})
            
            for doc_id, message_data in chat_data.items():
                if message_data.get('user_id') == user_id:
                    message_data['id'] = doc_id
                    all_messages.append(message_data)
            
            # Sort by timestamp (newest first)
            all_messages.sort(key=lambda x: x.get('timestamp', datetime.min), reverse=True)
            
            # Apply pagination
            paginated_messages = all_messages[offset:offset + limit]
            
            # Group messages into conversations
            conversations = group_messages_into_conversations(paginated_messages)
            
            return jsonify({
                'conversations': conversations,
                'total_messages': len(all_messages),
                'has_more': len(all_messages) > offset + limit,
                'pagination': {
                    'limit': limit,
                    'offset': offset,
                    'total': len(all_messages)
                }
            }), 200
        
        else:  # Real Firebase
            # Query with filters and pagination
            query = (chat_messages_ref
                    .where('user_id', '==', user_id)
                    .where('timestamp', '>=', start_date)
                    .where('timestamp', '<=', end_date)
                    .order_by('timestamp', direction='DESCENDING')
                    .limit(limit)
                    .offset(offset))
            
            docs = query.stream()
            messages = []
            
            for doc in docs:
                message_data = doc.to_dict()
                message_data['id'] = doc.id
                messages.append(message_data)
            
            # Group messages into conversations
            conversations = group_messages_into_conversations(messages)
            
            # Get total count for pagination
            total_query = (chat_messages_ref
                          .where('user_id', '==', user_id)
                          .where('timestamp', '>=', start_date)
                          .where('timestamp', '<=', end_date))
            
            total_docs = list(total_query.stream())
            total_count = len(total_docs)
            
            return jsonify({
                'conversations': conversations,
                'total_messages': total_count,
                'has_more': total_count > offset + limit,
                'pagination': {
                    'limit': limit,
                    'offset': offset,
                    'total': total_count
                }
            }), 200
            
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}")
        return jsonify({'error': 'Failed to fetch chat history'}), 500

@chat_history_bp.route('/conversations', methods=['GET'])
@require_auth
def get_conversations():
    """Get conversation summaries for the current user"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401
        
        limit = request.args.get('limit', 20, type=int)
        
        logger.info(f"Fetching conversations for user {user_id}")
        
        # Get all messages for the user
        chat_messages_ref = db.collection("chat_messages")
        
        if hasattr(db, 'data'):  # Mock database
            all_messages = []
            chat_data = db.data.get("chat_messages", {})
            
            for doc_id, message_data in chat_data.items():
                if message_data.get('user_id') == user_id:
                    message_data['id'] = doc_id
                    all_messages.append(message_data)
            
            # Sort by timestamp
            all_messages.sort(key=lambda x: x.get('timestamp', datetime.min), reverse=True)
            
        else:  # Real Firebase
            query = (chat_messages_ref
                    .where('user_id', '==', user_id)
                    .order_by('timestamp', direction='DESCENDING'))
            
            docs = query.stream()
            all_messages = []
            
            for doc in docs:
                message_data = doc.to_dict()
                message_data['id'] = doc.id
                all_messages.append(message_data)
        
        # Group into conversations and create summaries
        conversations = group_messages_into_conversations(all_messages)
        conversation_summaries = []
        
        for conv in conversations[:limit]:
            summary = create_conversation_summary(conv)
            conversation_summaries.append(summary)
        
        return jsonify({
            'conversations': conversation_summaries,
            'total': len(conversations)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching conversations: {e}")
        return jsonify({'error': 'Failed to fetch conversations'}), 500

@chat_history_bp.route('/conversation/<conversation_id>', methods=['GET'])
@require_auth
def get_conversation_details(conversation_id):
    """Get detailed messages for a specific conversation"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401
        
        logger.info(f"Fetching conversation {conversation_id} for user {user_id}")
        
        # For simplicity, we'll use timestamp-based conversation IDs
        # In a real implementation, you might want to store conversation IDs explicitly
        
        # Get messages around the conversation timestamp
        try:
            conv_timestamp = datetime.fromisoformat(conversation_id.replace('Z', '+00:00'))
        except:
            return jsonify({'error': 'Invalid conversation ID'}), 400
        
        # Get messages within a time window around the conversation
        start_time = conv_timestamp - timedelta(minutes=30)
        end_time = conv_timestamp + timedelta(minutes=30)
        
        chat_messages_ref = db.collection("chat_messages")
        
        if hasattr(db, 'data'):  # Mock database
            messages = []
            chat_data = db.data.get("chat_messages", {})
            
            for doc_id, message_data in chat_data.items():
                if (message_data.get('user_id') == user_id and 
                    start_time <= message_data.get('timestamp', datetime.min) <= end_time):
                    message_data['id'] = doc_id
                    messages.append(message_data)
            
        else:  # Real Firebase
            query = (chat_messages_ref
                    .where('user_id', '==', user_id)
                    .where('timestamp', '>=', start_time)
                    .where('timestamp', '<=', end_time)
                    .order_by('timestamp'))
            
            docs = query.stream()
            messages = []
            
            for doc in docs:
                message_data = doc.to_dict()
                message_data['id'] = doc.id
                messages.append(message_data)
        
        return jsonify({
            'conversation_id': conversation_id,
            'messages': messages,
            'message_count': len(messages)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching conversation details: {e}")
        return jsonify({'error': 'Failed to fetch conversation details'}), 500

@chat_history_bp.route('/search', methods=['GET'])
@require_auth
def search_chat_history():
    """Search through chat history"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401
        
        query_text = request.args.get('q', '').strip()
        if not query_text:
            return jsonify({'error': 'Search query required'}), 400
        
        limit = request.args.get('limit', 20, type=int)
        
        logger.info(f"Searching chat history for user {user_id}, query: {query_text}")
        
        # Get all messages for the user
        chat_messages_ref = db.collection("chat_messages")
        
        if hasattr(db, 'data'):  # Mock database
            all_messages = []
            chat_data = db.data.get("chat_messages", {})
            
            for doc_id, message_data in chat_data.items():
                if message_data.get('user_id') == user_id:
                    message_data['id'] = doc_id
                    all_messages.append(message_data)
            
        else:  # Real Firebase
            query = chat_messages_ref.where('user_id', '==', user_id)
            docs = query.stream()
            all_messages = []
            
            for doc in docs:
                message_data = doc.to_dict()
                message_data['id'] = doc.id
                all_messages.append(message_data)
        
        # Simple text search (in a real implementation, you might use full-text search)
        matching_messages = []
        query_lower = query_text.lower()
        
        for message in all_messages:
            content = message.get('content', '').lower()
            if query_lower in content:
                matching_messages.append(message)
        
        # Sort by timestamp (newest first)
        matching_messages.sort(key=lambda x: x.get('timestamp', datetime.min), reverse=True)
        
        # Apply limit
        limited_messages = matching_messages[:limit]
        
        return jsonify({
            'query': query_text,
            'messages': limited_messages,
            'total_matches': len(matching_messages),
            'showing': len(limited_messages)
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching chat history: {e}")
        return jsonify({'error': 'Failed to search chat history'}), 500

@chat_history_bp.route('/clear', methods=['POST'])
@require_auth
def clear_chat_history():
    """Clear all chat history for the current user"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401
        
        logger.info(f"Clearing chat history for user {user_id}")
        
        chat_messages_ref = db.collection("chat_messages")
        
        if hasattr(db, 'data'):  # Mock database
            chat_data = db.data.get("chat_messages", {})
            messages_to_delete = []
            
            for doc_id, message_data in chat_data.items():
                if message_data.get('user_id') == user_id:
                    messages_to_delete.append(doc_id)
            
            for doc_id in messages_to_delete:
                del chat_data[doc_id]
            
            deleted_count = len(messages_to_delete)
            
        else:  # Real Firebase
            query = chat_messages_ref.where('user_id', '==', user_id)
            docs = query.stream()
            
            deleted_count = 0
            for doc in docs:
                doc.reference.delete()
                deleted_count += 1
        
        return jsonify({
            'message': 'Chat history cleared successfully',
            'deleted_messages': deleted_count
        }), 200
        
    except Exception as e:
        logger.error(f"Error clearing chat history: {e}")
        return jsonify({'error': 'Failed to clear chat history'}), 500

def group_messages_into_conversations(messages, time_gap_minutes=30):
    """Group messages into conversations based on time gaps"""
    if not messages:
        return []
    
    conversations = []
    current_conversation = []
    
    for i, message in enumerate(messages):
        if i == 0:
            current_conversation = [message]
        else:
            # Check time gap between messages
            current_time = message.get('timestamp', datetime.min)
            prev_time = messages[i-1].get('timestamp', datetime.min)
            
            if isinstance(current_time, str):
                current_time = datetime.fromisoformat(current_time.replace('Z', '+00:00'))
            if isinstance(prev_time, str):
                prev_time = datetime.fromisoformat(prev_time.replace('Z', '+00:00'))
            
            time_diff = abs((current_time - prev_time).total_seconds() / 60)
            
            if time_diff > time_gap_minutes:
                # Start new conversation
                if current_conversation:
                    conversations.append(current_conversation)
                current_conversation = [message]
            else:
                # Continue current conversation
                current_conversation.append(message)
    
    # Add the last conversation
    if current_conversation:
        conversations.append(current_conversation)
    
    return conversations

def create_conversation_summary(conversation_messages):
    """Create a summary for a conversation"""
    if not conversation_messages:
        return None
    
    # Sort messages by timestamp
    sorted_messages = sorted(conversation_messages, 
                           key=lambda x: x.get('timestamp', datetime.min))
    
    first_message = sorted_messages[0]
    last_message = sorted_messages[-1]
    
    # Get first user message for title
    user_messages = [msg for msg in sorted_messages if msg.get('sender') == 'user']
    title = "New Conversation"
    if user_messages:
        first_user_content = user_messages[0].get('content', '')
        title = first_user_content[:50] + ('...' if len(first_user_content) > 50 else '')
    
    # Count messages by type
    user_count = len([msg for msg in conversation_messages if msg.get('sender') == 'user'])
    bot_count = len([msg for msg in conversation_messages if msg.get('sender') == 'bot'])
    
    return {
        'id': first_message.get('timestamp', datetime.now()).isoformat(),
        'title': title,
        'message_count': len(conversation_messages),
        'user_messages': user_count,
        'bot_messages': bot_count,
        'start_time': first_message.get('timestamp'),
        'last_time': last_message.get('timestamp'),
        'preview': last_message.get('content', '')[:100] + ('...' if len(last_message.get('content', '')) > 100 else '')
    }

