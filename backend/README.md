# AI Agent Backend

## Structure

### Core Files
- `app.py` - Main Flask application (full version)
- `app_minimal.py` - Minimal Flask app for stable deployment
- `Procfile` - Render deployment configuration
- `requirements.txt` - Python dependencies
- `runtime.txt` - Python version specification

### Directories
- `routes/` - API route handlers
  - `auth.py` - Authentication endpoints
  - `chat.py` - Chat functionality
  - `media.py` - Media handling
  - `chat_history.py` - Chat history management
  - `dl_routes.py` - Deep learning routes
  - `chats.py` - Chat management

- `core/` - Core functionality
  - Configuration and managers

- `agents/` - AI agent implementations
- `tools/` - Utility tools

### Configuration
- `.env` - Environment variables (not in git)
- `firebase_config.py` - Firebase configuration
- `render.yaml` - Render platform config

## Deployment
Currently deployed on Render using `app_minimal.py` for stability.

## Endpoints
- `/api/auth/*` - Authentication
- `/api/chat` - Chat interface
- `/api/media/*` - Media uploads
- `/api/health` - Health check