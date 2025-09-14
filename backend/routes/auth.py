from functools import wraps
from flask import Blueprint, request, jsonify, session
from flask_cors import cross_origin
import logging
import os
from werkzeug.security import generate_password_hash, check_password_hash
try:
    from firebase_config import db, get_cached_user, invalidate_user_cache, get_firestore_client
except:
    from firebase_config_mock import db
    # Fallback functions for mock
    def get_cached_user(user_id, ttl_seconds=300):
        users_ref = db.collection('users')
        user_doc = users_ref.document(user_id).get()
        if user_doc.exists:
            return {'id': user_doc.id, 'data': user_doc.to_dict(), 'exists': True}
        return {'exists': False}
    
    def invalidate_user_cache(user_id=None):
        pass
    
    def get_firestore_client():
        return db

from datetime import datetime, timedelta
import re
from functools import lru_cache

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

@auth_bp.route('/register', methods=['POST', 'OPTIONS'])
@cross_origin()
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validation
        if not username:
            return jsonify({'error': 'Username is required'}), 400
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters long'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        is_valid, password_message = validate_password(password)
        if not is_valid:
            return jsonify({'error': password_message}), 400
        
        # Optimized existence check with single batch query
        db_client = get_firestore_client()
        users_ref = db_client.collection('users')
        
        # Use batch to check both username and email in one query
        import asyncio
        
        # Check username
        username_docs = list(users_ref.where('username', '==', username).limit(1).stream())
        if username_docs:
            return jsonify({'error': 'Username already exists'}), 409
            
        # Check email
        email_docs = list(users_ref.where('email', '==', email).limit(1).stream())
        if email_docs:
            return jsonify({'error': 'Email already registered'}), 409

        # Create new user
        hashed_password = generate_password_hash(password)
        new_user_ref = users_ref.document()
        new_user_id = new_user_ref.id
        new_user_ref.set({
            'username': username,
            'email': email,
            'hashed_password': hashed_password
        })
        
        # Auto-login the user after successful registration
        session['user_id'] = new_user_id
        session['username'] = username
        session['login_time'] = datetime.utcnow().isoformat()
        session.permanent = True
        
        return jsonify({
            'message': 'User registered and logged in successfully',
            'user': {
                'id': new_user_id,
                'uid': new_user_id,  # Include both for compatibility
                'username': username,
                'email': email
            }
        }), 201
            
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
@cross_origin()
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Optimized user lookup with single query
        db_client = get_firestore_client()
        users_ref = db_client.collection('users')
        user_docs = list(users_ref.where('username', '==', username).limit(1).stream())
        
        if not user_docs:
            return jsonify({'error': 'Invalid username or password'}), 401
        
        user_snapshot = user_docs[0]
        user_data = user_snapshot.to_dict()
        
        if not check_password_hash(user_data['hashed_password'], password):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Store user session with timestamp
        session['user_id'] = user_snapshot.id
        session['username'] = user_data['username']
        session['login_time'] = datetime.utcnow().isoformat()
        session.permanent = True  # Make session persistent
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user_snapshot.id,
                'uid': user_snapshot.id,  # Include both for compatibility
                'username': user_data['username'],
                'email': user_data['email']
            }
        }), 200
            
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST', 'OPTIONS'])
@cross_origin()
def logout():
    """Logout user"""
    try:
        # Clear session data
        session.clear()
        session.modified = True
        
        # Create response
        response = jsonify({'message': 'Logout successful'})
        
        # Clear session cookie with proper settings
        is_production = os.getenv('FLASK_ENV') == 'production' or os.getenv('RENDER')
        
        if is_production:
            response.set_cookie(
                'session', 
                '', 
                expires=0, 
                httponly=True, 
                secure=True,
                samesite='None'
            )
        else:
            response.set_cookie(
                'session', 
                '', 
                expires=0, 
                httponly=True, 
                secure=False,
                samesite='Lax'
            )
        
        return response, 200
    except Exception as e:
        return jsonify({'error': f'Logout failed: {str(e)}'}), 500

@auth_bp.route('/debug-session')
def debug_session():
    return jsonify(dict(session)), 200

@auth_bp.route('/check-auth', methods=['GET', 'OPTIONS'])
@cross_origin()
def check_auth():
    """Super fast auth check with caching and optimized session handling"""
    try:
        if 'user_id' not in session:
            return jsonify({'authenticated': False, 'reason': 'no_session'}), 200
            
        # Extended session timeout to 2 hours for better UX
        if 'login_time' in session:
            login_time = datetime.fromisoformat(session['login_time'])
            session_age = (datetime.utcnow() - login_time).total_seconds()
            
            if session_age > 7200:  # 2 hours instead of 30 minutes
                session.clear()
                session.modified = True
                return jsonify({'authenticated': False, 'reason': 'session_expired'}), 200
        
        user_id = session['user_id']
        
        # Use cached user data instead of hitting database every time
        cached_user = get_cached_user(user_id, ttl_seconds=600)  # 10 minute cache
        
        if cached_user['exists']:
            user_data = cached_user['data']
            # Update last activity time less frequently (every 5 minutes)
            current_time = datetime.utcnow()
            
            if 'last_activity_update' not in session:
                session['last_activity_update'] = current_time.isoformat()
                session['last_activity'] = current_time.isoformat()
            else:
                last_update = datetime.fromisoformat(session['last_activity_update'])
                if (current_time - last_update).total_seconds() > 300:  # 5 minutes
                    session['last_activity_update'] = current_time.isoformat()
                    session['last_activity'] = current_time.isoformat()
            
            return jsonify({
                'authenticated': True,
                'user': {
                    'id': cached_user['id'],
                    'uid': cached_user['id'],  # Include both for compatibility
                    'username': user_data['username'],
                    'email': user_data['email']
                }
            }), 200
        else:
            # User not found in database, clear session
            session.clear()
            session.modified = True
            return jsonify({'authenticated': False, 'reason': 'user_not_found'}), 200
            
    except Exception as e:
        logging.error(f"Auth check error: {e}")
        # Don't clear session on temporary errors, just return false
        return jsonify({'authenticated': False, 'error': f'Auth check failed: {str(e)}'}), 500

def require_auth(func):
    """Optimized auth decorator with caching"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Use cached user check instead of database hit every time
        try:
            cached_user = get_cached_user(user_id, ttl_seconds=300)  # 5 minute cache
            if not cached_user['exists']:
                session.clear()
                session.modified = True
                return jsonify({'error': 'Authentication required'}), 401
        except Exception as e:
            logging.error(f"Auth check error in decorator: {e}")
            return jsonify({'error': 'Authentication required'}), 401
        
        return func(*args, **kwargs)
    return wrapper

# Add cache invalidation on logout and user updates
@auth_bp.after_request
def after_request(response):
    """Clear relevant caches after certain operations"""
    if request.endpoint in ['auth.logout']:
        user_id = session.get('user_id')
        if user_id:
            invalidate_user_cache(user_id)
    return response


