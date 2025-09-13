from flask import Flask, session, jsonify, request
from flask_cors import CORS
from routes.auth import auth_bp
from routes.chat import chat_bp
from routes.media import media_bp
from routes.chat_history import chat_history_bp
from routes.dl_routes import dl_bp
from routes.chats import chats_bp
from core.model_manager_lite import model_manager
from core.llm_manager_fixed import create_llm_manager
from core.config import settings

import os
import logging
from datetime import timedelta

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configuration - Environment-specific settings with better session handling
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production-12345')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)  # Extended to 2 hours
    
    # Session configuration for better performance
    app.config['SESSION_PERMANENT'] = True
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_KEY_PREFIX'] = 'binarybrained:'
    
    # Session cookie settings - different for development vs production
    is_production = os.getenv('FLASK_ENV') == 'production' or os.getenv('RENDER')
    
    if is_production:
        # Production settings for HTTPS deployment
        app.config['SESSION_COOKIE_SECURE'] = True
        app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    else:
        # Development settings for HTTP
        app.config['SESSION_COOKIE_SECURE'] = False
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_DOMAIN'] = None
    
    # File upload settings
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = 'uploads'

    # Enhanced CORS configuration with wildcard for Vercel deployments
    allowed_origins = [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'https://ai-agent-with-frontend.onrender.com',
        'https://ai-agent-zeta-bice.vercel.app',
        'https://*.vercel.app'  # Allow all Vercel preview deployments
    ]

    CORS(app,
        resources={
            r"/api/*": {
                "origins": allowed_origins,
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                "allow_headers": ["Content-Type", "Authorization", "Cookie", "X-Requested-With", "Accept", "Origin"],
                "supports_credentials": True,
                "expose_headers": ["Set-Cookie", "Content-Range", "X-Content-Range"],
                "max_age": 3600
            }
        },
        send_wildcard=False,
        always_send=True
    )

    # Additional OPTIONS handler for preflight requests
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = jsonify({'status': 'ok'})
            response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, Cookie, X-Requested-With, Accept, Origin')
            response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, PATCH')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            response.headers.add('Access-Control-Max-Age', '3600')
            return response, 200

    # After request handler to ensure CORS headers are always present
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if origin in allowed_origins or (origin and origin.endswith('.vercel.app')):
            response.headers.add('Access-Control-Allow-Origin', origin)
            response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(media_bp, url_prefix='/api/media')
    app.register_blueprint(chat_history_bp, url_prefix='/api/chat-history')
    app.register_blueprint(chats_bp)
    app.register_blueprint(dl_bp)
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {
            'status': 'ok', 
            'message': 'AI Agent API is running',
            'version': '2.0.0',
            'features': [
                'chat',
                'media_upload',
                'chat_history',
                'deep_learning',
                'improved_ui'
            ]
        }
    
    @app.route('/')
    def root():
        return {
            'message': 'AI Agent API v2.0 is running',
            'endpoints': [
                '/api/health',
                '/api/auth/*',
                '/api/chat',
                '/api/media/*',
                '/api/chat-history/*'
            ]
        }
    
    # Error handlers
    @app.errorhandler(413)
    def too_large(e):
        return {'error': 'File too large. Maximum size is 16MB.'}, 413
    
    @app.errorhandler(404)
    def not_found(e):
        return {'error': 'Endpoint not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(e):
        return {'error': 'Internal server error'}, 500
    
    # Initialize models and LLM manager on startup
    with app.app_context():
        initialize_models()
        initialize_llm_manager()

    return app

def initialize_models():
    """Initialize deep learning models on application startup"""
    try:
        logging.info("Model initialization completed")
    except Exception as e:
        logging.error(f"Failed to initialize models: {str(e)}")

def initialize_llm_manager():
    """Initialize LLM manager with improved error handling"""
    try:
        global llm_manager
        llm_manager = create_llm_manager(settings)
        logging.info("LLM manager initialized successfully")
        
        # Test the LLM manager
        status = llm_manager.get_status()
        logging.info(f"LLM Manager Status: {status}")
        
    except Exception as e:
        logging.error(f"Failed to initialize LLM manager: {str(e)}")

# Create the app instance for imports
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)