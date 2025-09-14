from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello from Render! Backend is working!'

@app.route('/api/health')
def health():
    return {'status': 'ok', 'message': 'Basic backend is running'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)