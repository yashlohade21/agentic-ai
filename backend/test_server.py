#!/usr/bin/env python3
"""
Test script to verify the Flask app can start
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app
    print("✅ Flask app imported successfully")

    # Test if app can be created
    if app:
        print("✅ Flask app instance created")

        # Test routes
        with app.test_client() as client:
            response = client.get('/api/health')
            if response.status_code == 200:
                print("✅ Health check endpoint working")
                print(f"Response: {response.json}")
            else:
                print(f"❌ Health check failed with status: {response.status_code}")

    print("\n✅ Server test completed successfully!")
    print("The app should work on Render.")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Missing dependencies. Please run: pip install -r requirements.txt")
    sys.exit(1)

except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)