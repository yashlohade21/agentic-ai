from flask import Flask, session
from flask_cors import CORS
from routes.auth import auth_bp
from routes.chat import chat_bp
from routes.dl_routes import dl_bp  # Import the new deep learning blueprint
from core.model_manager_lite import model_manager # Import model manager

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
    
    # Configuration - Environment-specific settings
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production-12345')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # 30 minutes instead of 24 hours
    
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
    app.config['SESSION_COOKIE_DOMAIN'] = None  # Allow subdomain sharing

    # Enable CORS for all routes with proper session support
    CORS(app, 
         supports_credentials=True, 
         origins=[
             'http://localhost:3000', 
             'http://127.0.0.1:3000',
             'http://localhost:5173',
             'http://127.0.0.1:5173',
             'https://ai-agent-with-frontend.onrender.com',
             'https://ai-agent-zeta-bice.vercel.app',
         ],
         allow_headers=['Content-Type', 'Authorization', 'Cookie', 'X-Requested-With'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         expose_headers=['Set-Cookie'],
         send_wildcard=False
    )
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(dl_bp) # Register the deep learning blueprint
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {'status': 'ok', 'message': 'AI Agent API is running'}
    
    @app.route('/')
    def root():
        return {'message': 'AI Agent API is running'}
    
    # Initialize models on startup
    with app.app_context():
        initialize_models()

    return app

def initialize_models():
    """Initialize deep learning models on application startup"""
    try:
        # Example: Load a pre-trained sentiment analysis model
        # model_manager.load_huggingface_model('sentiment_analyzer', 'cardiffnlp/twitter-roberta-base-sentiment-latest')
        
        # Example: Load a custom TensorFlow model
        # model_manager.load_tensorflow_model('image_classifier', 'models/weights/my_classifier.h5')
        
        # Example: Load a PyTorch model
        # model_manager.load_pytorch_model('custom_model', 'models/weights/my_pytorch_model.pt')
        
        logging.info("Model initialization completed")
        
    except Exception as e:
        logging.error(f"Failed to initialize models: {str(e)}")

# Create the app instance for imports
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


