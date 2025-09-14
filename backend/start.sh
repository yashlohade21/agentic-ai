#!/bin/bash

# Set environment variables
export FLASK_ENV=production
export PYTHONPATH=.

# Start the server with gunicorn
if [ -z "$PORT" ]; then
    export PORT=5000
fi

echo "Starting server on port $PORT..."
gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --preload
