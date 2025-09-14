from flask import Flask, session, jsonify, request
from flask_cors import CORS, cross_origin
import os
import logging
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash

# Simple user storage for now (replace with proper database later)
USERS_DB = {}

def create_app():
    """Create and configure Flask application for production"""
    app = Flask(__name__)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'production-secret-key-change-this')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
    
    # Session configuration
    app.config['SESSION_PERMANENT'] = True
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_KEY_PREFIX'] = 'aiagent:'
    
    # Production session settings
    is_production = os.getenv('FLASK_ENV') == 'production' or os.getenv('RENDER')
    if is_production:
        app.config['SESSION_COOKIE_SECURE'] = True
        app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    else:
        app.config['SESSION_COOKIE_SECURE'] = False
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_DOMAIN'] = None
    
    # File upload settings
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
    
    # CORS configuration
    allowed_origins = [
        "https://ai-agent-zeta-bice.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    CORS(app, resources={r"/*": {
        "origins": allowed_origins,
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
        "expose_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    }})
    
    # Handle preflight requests
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = jsonify({})
            origin = request.headers.get('Origin')
            if origin in allowed_origins:
                response.headers.add("Access-Control-Allow-Origin", origin)
            response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,X-Requested-With,Accept,Origin")
            response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS,PATCH")
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            response.headers.add('Access-Control-Max-Age', '86400')
            return response
    
    # Routes
    @app.route('/')
    def root():
        return jsonify({
            'message': 'AI Agent API v2.0 Production',
            'status': 'running',
            'environment': os.getenv('FLASK_ENV', 'development'),
            'cors_enabled': True
        })
    
    @app.route('/api/health')
    @cross_origin()
    def health_check():
        return jsonify({
            'status': 'ok',
            'message': 'AI Agent API is running',
            'version': '2.0.0',
            'cors_enabled': True,
            'environment': os.getenv('FLASK_ENV', 'development')
        })
    
    @app.route('/ping')
    def ping():
        return 'pong', 200
    
    # Auth Routes
    @app.route('/api/auth/check-auth', methods=['GET', 'OPTIONS'])
    @cross_origin()
    def check_auth():
        try:
            if 'user_id' in session:
                return jsonify({
                    'authenticated': True,
                    'user': {
                        'id': session['user_id'],
                        'username': session.get('username', 'User')
                    }
                })
            return jsonify({'authenticated': False})
        except Exception as e:
            logging.error(f"Auth check error: {e}")
            return jsonify({'authenticated': False, 'error': str(e)}), 500
    
    @app.route('/api/auth/register', methods=['POST', 'OPTIONS'])
    @cross_origin()
    def register():
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '')
            
            if not username or not email or not password:
                return jsonify({'error': 'All fields are required'}), 400
            
            if len(username) < 3:
                return jsonify({'error': 'Username must be at least 3 characters'}), 400
            
            if username in USERS_DB:
                return jsonify({'error': 'Username already exists'}), 409
            
            # Create user
            user_id = f"user_{len(USERS_DB) + 1}"
            USERS_DB[username] = {
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
            
        except Exception as e:
            logging.error(f"Registration error: {e}")
            return jsonify({'error': f'Registration failed: {str(e)}'}), 500
    
    @app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
    @cross_origin()
    def login():
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            username = data.get('username', '').strip()
            password = data.get('password', '')
            
            if not username or not password:
                return jsonify({'error': 'Username and password are required'}), 400
            
            if username not in USERS_DB:
                return jsonify({'error': 'Invalid credentials'}), 401
            
            user = USERS_DB[username]
            if not check_password_hash(user['password'], password):
                return jsonify({'error': 'Invalid credentials'}), 401
            
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
            
        except Exception as e:
            logging.error(f"Login error: {e}")
            return jsonify({'error': f'Login failed: {str(e)}'}), 500
    
    @app.route('/api/auth/logout', methods=['POST', 'OPTIONS'])
    @cross_origin()
    def logout():
        try:
            session.clear()
            return jsonify({'message': 'Logged out successfully'})
        except Exception as e:
            logging.error(f"Logout error: {e}")
            return jsonify({'error': f'Logout failed: {str(e)}'}), 500
    
    # Chat endpoint (basic)
    @app.route('/api/chat', methods=['POST', 'OPTIONS'])
    @cross_origin()
    def chat():
        try:
            data = request.get_json()
            message = data.get('message', '')
            
            # Simple echo response for now
            return jsonify({
                'response': f"Echo: {message}",
                'timestamp': 'now'
            })
        except Exception as e:
            logging.error(f"Chat error: {e}")
            return jsonify({'error': f'Chat failed: {str(e)}'}), 500
    
    @app.route('/api/chats', methods=['GET', 'OPTIONS'])
    @cross_origin()
    def get_chats():
        return jsonify({'chats': []})
    
    # Error handlers
    @app.errorhandler(413)
    def too_large(e):
        return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)