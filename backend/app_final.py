from flask import Flask, jsonify, request, session
import os
from datetime import timedelta

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'production-secret-key')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

# Simple CORS implementation
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    allowed_origins = [
        'https://ai-agent-zeta-bice.vercel.app',
        'http://localhost:3000',
        'http://localhost:5173'
    ]
    
    if origin in allowed_origins:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    
    return response

@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        response = jsonify({})
        origin = request.headers.get('Origin')
        allowed_origins = [
            'https://ai-agent-zeta-bice.vercel.app',
            'http://localhost:3000',
            'http://localhost:5173'
        ]
        
        if origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        
        return response

# Simple user storage
USERS = {}

@app.route('/')
def home():
    return jsonify({
        'message': 'AI Agent Backend is running!',
        'status': 'success',
        'cors': 'enabled'
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
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': session['user_id'],
                'username': session.get('username', 'User')
            }
        })
    return jsonify({'authenticated': False})

@app.route('/api/auth/register', methods=['POST', 'OPTIONS'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not username or not email or not password:
        return jsonify({'error': 'All fields required'}), 400
    
    if username in USERS:
        return jsonify({'error': 'Username exists'}), 409
    
    user_id = f'user_{len(USERS) + 1}'
    USERS[username] = {
        'id': user_id,
        'email': email,
        'password': password  # Note: In production, hash this!
    }
    
    session['user_id'] = user_id
    session['username'] = username
    session.permanent = True
    
    return jsonify({
        'message': 'Registration successful',
        'user': {'id': user_id, 'username': username, 'email': email}
    }), 201

@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    if username not in USERS or USERS[username]['password'] != password:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    user = USERS[username]
    session['user_id'] = user['id']
    session['username'] = username
    session.permanent = True
    
    return jsonify({
        'message': 'Login successful',
        'user': {'id': user['id'], 'username': username}
    })

@app.route('/api/auth/logout', methods=['POST', 'OPTIONS'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    return jsonify({
        'response': f'Echo: {message}',
        'timestamp': 'now'
    })

@app.route('/api/chats', methods=['GET', 'OPTIONS'])
def get_chats():
    return jsonify({'chats': []})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)