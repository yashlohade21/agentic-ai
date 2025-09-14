from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
import logging
from datetime import timedelta
import secrets

app = Flask(__name__)

# Basic configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production-12345')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

# Simple CORS setup - THIS WILL FIX THE CORS ERROR
CORS(app,
     origins=[
         'http://localhost:3000',
         'http://localhost:5173',
         'https://ai-agent-zeta-bice.vercel.app'
     ],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization'],
     supports_credentials=True
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple user storage (in production, use a real database)
USERS = {
    'admin': {'password': 'admin123', 'email': 'admin@example.com'},
    'user': {'password': 'user123', 'email': 'user@example.com'}
}

@app.route('/')
def home():
    return {'message': 'AI Agent API is running!', 'status': 'ok'}

@app.route('/ping')
def ping():
    return 'pong'

@app.route('/api/health')
def health():
    return {
        'status': 'ok',
        'message': 'AI Agent API is running',
        'version': '1.0.0',
        'cors_enabled': True
    }

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        logger.info(f"Login attempt for username: {username}")

        # Simple authentication
        if username in USERS and USERS[username]['password'] == password:
            session['user'] = username
            session['authenticated'] = True
            session.permanent = True

            logger.info(f"Login successful for: {username}")
            return jsonify({
                'success': True,
                'user': {
                    'username': username,
                    'email': USERS[username]['email']
                }
            })
        else:
            logger.warning(f"Login failed for: {username}")
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'success': False, 'error': 'Login failed'}), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        if username in USERS:
            return jsonify({'success': False, 'error': 'Username already exists'}), 400

        # Add user (in production, hash the password!)
        USERS[username] = {'password': password, 'email': email}

        logger.info(f"User registered: {username}")
        return jsonify({'success': True, 'message': 'User registered successfully'})

    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'success': False, 'error': 'Registration failed'}), 500

@app.route('/api/auth/check-auth', methods=['GET'])
def check_auth():
    try:
        if session.get('authenticated') and session.get('user'):
            username = session.get('user')
            return jsonify({
                'authenticated': True,
                'user': {
                    'username': username,
                    'email': USERS.get(username, {}).get('email', '')
                }
            })
        else:
            return jsonify({'authenticated': False})

    except Exception as e:
        logger.error(f"Auth check error: {e}")
        return jsonify({'authenticated': False})

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        if not session.get('authenticated'):
            return jsonify({'error': 'Not authenticated'}), 401

        data = request.get_json()
        message = data.get('message', '')

        # Simple echo response (replace with actual AI logic)
        response = f"Echo: {message}. This is a simple response from the backend!"

        return jsonify({
            'response': response,
            'success': True
        })

    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({'error': 'Chat failed'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)