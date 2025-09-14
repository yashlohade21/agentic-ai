@echo off
REM Script to run the backend locally for development on Windows

echo Starting Flask backend server...
echo ================================

REM Set environment variables for local development
set FLASK_ENV=development
set FLASK_DEBUG=1

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Run the Flask app
echo Starting server on http://localhost:5000
python app.py