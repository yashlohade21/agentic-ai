from functools import wraps
from flask import Blueprint, request, jsonify, session
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Session
from database import get_db
from routes.models import User
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
        db = next(get_db())
        try:
            existing_user = db.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                if existing_user.username == username:
                    return jsonify({'error': 'Username already exists'}), 409
                else:
                    return jsonify({'error': 'Email already registered'}), 409
            
            # Create new user
            hashed_password = generate_password_hash(password)
            new_user = User(
                username=username,
                email=email,
                hashed_password=hashed_password
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # Auto-login the user after successful registration
            session['user_id'] = new_user.id
            session['username'] = new_user.username
            session.permanent = True
            
            return jsonify({
                'message': 'User registered and logged in successfully',
                'user': {
                    'id': new_user.id,
                    'username': new_user.username,
                    'email': new_user.email
                }
            }), 201
            
        except Exception as e:
            db.rollback()
            return jsonify({'error': f'Database error: {str(e)}'}), 500
        finally:
            db.close()
            
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
        db = next(get_db())
        try:
            user = db.query(User).filter(User.username == username).first()
            
            if not user or not check_password_hash(user.hashed_password, password):
                return jsonify({'error': 'Invalid username or password'}), 401
            
            # Store user session
            session['user_id'] = user.id
            session['username'] = user.username
            session.permanent = True  # Make session persistent
            
            return jsonify({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'Database error: {str(e)}'}), 500
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    try:
        session.clear()
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        return jsonify({'error': f'Logout failed: {str(e)}'}), 500

@auth_bp.route('/debug-session', methods=['GET'])
def debug_session():
    """Debug endpoint to check session contents"""
    return jsonify({
        'session_contents': dict(session),
        'has_user_id': 'user_id' in session,
        'user_id': session.get('user_id')
    }), 200

@auth_bp.route('/check-auth', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    try:
        if 'user_id' in session:
            db = next(get_db())
            try:
                user = db.query(User).filter(User.id == session['user_id']).first()
                if user:
                    return jsonify({
                        'authenticated': True,
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email
                        }
                    }), 200
                else:
                    session.clear()
                    return jsonify({'authenticated': False}), 200
            finally:
                db.close()
        else:
            return jsonify({'authenticated': False}), 200
    except Exception as e:
        return jsonify({'error': f'Auth check failed: {str(e)}'}), 500

def require_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        logging.info(f"Auth check - Session contents: {dict(session)}")
        logging.info(f"Auth check - User ID: {user_id}")
        if not user_id:
            logging.warning("Unauthorized access attempt: session empty")
            return jsonify({'error': 'Authentication required'}), 401
        return func(*args, **kwargs)
    return wrapper
