from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)

# CORS configuration with specific frontend domains
allowed_origins = [
    "https://ai-agent-zeta-bice.vercel.app",  # Production frontend
    "http://localhost:3000",  # Local development
    "http://localhost:5173",  # Vite dev server
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

@app.route('/')
def index():
    return jsonify({
        'message': 'AI Agent Backend Test Version',
        'status': 'running',
        'cors_enabled': True
    })

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'ok',
        'message': 'API is running',
        'cors_enabled': True,
        'environment': os.getenv('FLASK_ENV', 'development')
    })

@app.route('/api/auth/check-auth', methods=['GET'])
def check_auth():
    return jsonify({
        'authenticated': False,
        'message': 'Test endpoint - no real auth implemented'
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    return jsonify({
        'error': 'Test endpoint - login not implemented in test version'
    }), 501

@app.route('/api/auth/register', methods=['POST'])
def register():
    return jsonify({
        'error': 'Test endpoint - register not implemented in test version'
    }), 501

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
