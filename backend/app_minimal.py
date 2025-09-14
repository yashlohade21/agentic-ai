#!/usr/bin/env python3
"""Minimal Flask app for testing CORS"""

from flask import Flask, jsonify, request, session
from flask_cors import CORS
import os
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Basic configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

# Very permissive CORS for debugging
CORS(app, resources={r"/*": {
    "origins": "*",
    "allow_headers": "*",
    "expose_headers": "*",
    "supports_credentials": True,
    "methods": "*"
}})

# Add CORS headers to every response
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin'
    response.headers['Access-Control-Max-Age'] = '3600'
    return response

# Mock user storage
users_db = {}

@app.route('/')
def index():
    return jsonify({'message': 'AI Agent Backend (Minimal) is running'})

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'ok',
        'message': 'API is running',
        'cors_enabled': True
    })

@app.route('/api/auth/check-auth', methods=['GET'])
def check_auth():
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': session['user_id'],
                'username': session.get('username', 'User')
            }
        })
    return jsonify({'authenticated': False})

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400

    # Check if user exists
    if username in users_db:
        return jsonify({'error': 'Username already exists'}), 409

    # Create user
    user_id = f"user_{len(users_db) + 1}"
    users_db[username] = {
        'id': user_id,
        'email': email,
        'password': generate_password_hash(password)
    }

    # Auto-login
    session['user_id'] = user_id
    session['username'] = username
    session.permanent = True

    return jsonify({
        'message': 'User registered successfully',
        'user': {
            'id': user_id,
            'username': username,
            'email': email
        }
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    # Check user
    if username not in users_db:
        return jsonify({'error': 'Invalid credentials'}), 401

    user = users_db[username]
    if not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid credentials'}), 401

    # Login
    session['user_id'] = user['id']
    session['username'] = username
    session.permanent = True

    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user['id'],
            'username': username
        }
    })

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

# Chat endpoints (minimal implementation)
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')

    # Simple echo response for testing
    return jsonify({
        'response': f"Echo: {message}",
        'timestamp': 'now'
    })

@app.route('/api/chats', methods=['GET'])
def get_chats():
    return jsonify({'chats': []})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)