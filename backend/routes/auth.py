from functools import wraps
from flask import Blueprint, request, jsonify, session
import logging
import os
from werkzeug.security import generate_password_hash, check_password_hash
from firebase_config import db
from datetime import datetime
import re

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

@auth_bp.route('/register', methods=['POST'])
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
        
        # Check if user already exists
        users_ref = db.collection('users')
        username_query = users_ref.where('username', '==', username).limit(1).stream()
        email_query = users_ref.where('email', '==', email).limit(1).stream()

        if next(username_query, None):
            return jsonify({'error': 'Username already exists'}), 409
        if next(email_query, None):
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
                'username': username,
                'email': email
            }
        }), 201
            
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
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
        
        # Find user
        users_ref = db.collection('users')
        query = users_ref.where('username', '==', username).limit(1).stream()
        user_snapshot = next(query, None)

        if not user_snapshot:
            return jsonify({'error': 'Invalid username or password'}), 401

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
                'username': user_data['username'],
                'email': user_data['email']
            }
        }), 200
            
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
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

@auth_bp.route('/check-auth', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    try:
        if 'user_id' in session and 'login_time' in session:
            # Check session timeout (30 minutes)
            login_time = datetime.fromisoformat(session['login_time'])
            if (datetime.utcnow() - login_time).total_seconds() > 1800:  # 30 minutes
                session.clear()
                session.modified = True
                return jsonify({'authenticated': False, 'reason': 'session_expired'}), 200
            
            users_ref = db.collection('users')
            user_doc = users_ref.document(session['user_id']).get()

            if user_doc.exists:
                user_data = user_doc.to_dict()
                # Update last activity time
                session['last_activity'] = datetime.utcnow().isoformat()
                return jsonify({
                    'authenticated': True,
                    'user': {
                        'id': user_doc.id,
                        'username': user_data['username'],
                        'email': user_data['email']
                    }
                }), 200
            else:
                session.clear()
                session.modified = True
                return jsonify({'authenticated': False, 'reason': 'user_not_found'}), 200
        else:
            return jsonify({'authenticated': False, 'reason': 'no_session'}), 200
    except Exception as e:
        session.clear()
        session.modified = True
        return jsonify({'authenticated': False, 'error': f'Auth check failed: {str(e)}'}), 500

def require_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Additional check: verify user still exists in database
        try:
            users_ref = db.collection('users')
            user_doc = users_ref.document(user_id).get()
            if not user_doc.exists:
                session.clear()
                session.modified = True
                return jsonify({'error': 'Authentication required'}), 401
        except Exception as e:
            return jsonify({'error': 'Authentication required'}), 401
        
        return func(*args, **kwargs)
    return wrapper


