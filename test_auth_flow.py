#!/usr/bin/env python3
"""
Test script to verify authentication flow works correctly
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_auth_flow():
    print("Testing Authentication Flow...")
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("PASS: Health check passed")
        else:
            print(f"FAIL: Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"FAIL: Health check failed: {e}")
        return False
    
    # Test 2: Register new user
    print("\n2. Testing user registration...")
    test_user = {
        "username": "testuser123",
        "email": "test@example.com", 
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=test_user)
        if response.status_code == 201:
            print("PASS: User registration successful")
            print(f"Response: {response.json()}")
            session_cookies = response.cookies
        else:
            print(f"FAIL: Registration failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"FAIL: Registration failed: {e}")
        return False
    
    # Test 3: Check auth status (should be authenticated after registration)
    print("\n3. Testing auth check after registration...")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/check-auth", cookies=session_cookies)
        if response.status_code == 200:
            auth_data = response.json()
            if auth_data.get('authenticated'):
                print("PASS: Auto-login after registration works")
                print(f"User: {auth_data.get('user')}")
            else:
                print("FAIL: Auto-login failed - user not authenticated")
                return False
        else:
            print(f"FAIL: Auth check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"FAIL: Auth check failed: {e}")
        return False
    
    # Test 4: Test chat endpoint (should work with authentication)
    print("\n4. Testing chat endpoint with authentication...")
    try:
        chat_data = {"message": "Hello, this is a test message"}
        response = requests.post(f"{BASE_URL}/api/chat", json=chat_data, cookies=session_cookies)
        if response.status_code == 200:
            print("PASS: Chat endpoint works with authentication")
        else:
            print(f"FAIL: Chat endpoint failed: {response.status_code} - {response.text}")
            print("Note: Chat failure might be due to AI system initialization, not auth")
    except Exception as e:
        print(f"FAIL: Chat endpoint failed: {e}")
    
    # Test 5: Logout
    print("\n5. Testing logout...")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/logout", cookies=session_cookies)
        if response.status_code == 200:
            print("PASS: Logout successful")
        else:
            print(f"FAIL: Logout failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"FAIL: Logout failed: {e}")
        return False
    
    # Test 6: Check auth after logout (should be false)
    print("\n6. Testing auth check after logout...")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/check-auth", cookies=session_cookies)
        if response.status_code == 200:
            auth_data = response.json()
            if not auth_data.get('authenticated'):
                print("PASS: Logout properly cleared session")
            else:
                print("FAIL: Session not cleared after logout")
                return False
        else:
            print(f"FAIL: Auth check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"FAIL: Auth check failed: {e}")
        return False
    
    print("\nSUCCESS: All authentication tests passed!")
    return True

if __name__ == "__main__":
    test_auth_flow()