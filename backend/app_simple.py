from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)

# Simple CORS - allow all origins for testing
CORS(app, origins=['https://ai-agent-zeta-bice.vercel.app', 'http://localhost:3000', 'http://localhost:5173'])

@app.route('/')
def home():
    return jsonify({
        'message': 'Simple AI Agent Backend is WORKING!',
        'status': 'success',
        'timestamp': '2024-01-15'
    })

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'ok',
        'message': 'Health check passed',
        'cors': 'enabled'
    })

@app.route('/api/auth/check-auth', methods=['GET', 'OPTIONS'])
def check_auth():
    return jsonify({'authenticated': False, 'message': 'Simple version - no auth yet'})

@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    return jsonify({'message': 'Login endpoint working', 'success': False})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)