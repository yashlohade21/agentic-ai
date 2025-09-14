#!/usr/bin/env python3
"""Test CORS configuration for the backend API"""

import requests
import json

# Backend URL
BACKEND_URL = "https://ai-agent-with-frontend.onrender.com"
FRONTEND_ORIGIN = "https://ai-agent-zeta-bice.vercel.app"

def test_cors_preflight():
    """Test CORS preflight request"""
    print("Testing CORS preflight request...")

    # Test check-auth endpoint
    response = requests.options(
        f"{BACKEND_URL}/api/auth/check-auth",
        headers={
            "Origin": FRONTEND_ORIGIN,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type"
        }
    )

    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")

    # Check for CORS headers
    cors_headers = {
        'Access-Control-Allow-Origin',
        'Access-Control-Allow-Methods',
        'Access-Control-Allow-Headers',
        'Access-Control-Allow-Credentials'
    }

    for header in cors_headers:
        if header in response.headers:
            print(f"✓ {header}: {response.headers[header]}")
        else:
            print(f"✗ {header}: Missing")

def test_actual_request():
    """Test actual GET request with CORS"""
    print("\nTesting actual GET request...")

    response = requests.get(
        f"{BACKEND_URL}/api/auth/check-auth",
        headers={
            "Origin": FRONTEND_ORIGIN,
            "Content-Type": "application/json"
        }
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    if 'Access-Control-Allow-Origin' in response.headers:
        print(f"✓ CORS Origin: {response.headers['Access-Control-Allow-Origin']}")
    else:
        print("✗ CORS Origin header missing")

if __name__ == "__main__":
    print("=" * 50)
    print("CORS Configuration Test")
    print("=" * 50)

    test_cors_preflight()
    test_actual_request()

    print("\n" + "=" * 50)
    print("Test completed!")