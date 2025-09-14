#!/bin/bash

# Script to run the backend locally for development

echo "Starting Flask backend server..."
echo "================================"

# Set environment variables for local development
export FLASK_ENV=development
export FLASK_DEBUG=1

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the Flask app
echo "Starting server on http://localhost:5000"
python app.py