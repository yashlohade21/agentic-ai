from flask import Flask, session
from flask_cors import CORS
from routes.auth import auth_bp
from routes.chat import chat_bp
from database import Base, engine
import os
from datetime import timedelta

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    
    # Enable CORS for all routes
    CORS(app, supports_credentials=True, origins=[
    'http://localhost:3000', 
    'http://127.0.0.1:3000',
    'http://localhost:5173',
    'http://127.0.0.1:5173'
    ])
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(chat_bp, url_prefix='/api')
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {'status': 'ok', 'message': 'AI Agent API is running'}
    
    @app.route('/')
    def root():
        return {'message': 'AI Agent API is running'}
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified successfully")
    except Exception as e:
        print(f"❌ Database table creation failed: {e}")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)

