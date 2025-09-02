#!/usr/bin/env python3
"""
Test script for Django Authentication APIs
Run this script to test the signup, login, and profile endpoints
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_signup():
    """Test user signup"""
    print("Testing User Signup...")
    
    signup_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/signup/", json=signup_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        return response.json()['data']['token']
    return None

def test_login():
    """Test user login"""
    print("\nTesting User Login...")
    
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        return response.json()['data']['token']
    return None

def test_profile(token):
    """Test getting user profile with JWT token"""
    print("\nTesting User Profile...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_social_login():
    """Test social login"""
    print("\nTesting Social Login...")
    
    social_data = {
        "provider": "google",
        "social_id": "123456789",
        "email": "social@example.com",
        "name": "Social User"
    }
    
    response = requests.post(f"{BASE_URL}/auth/social/", json=social_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        return response.json()['data']['token']
    return None

def test_health():
    """Test health check endpoint"""
    print("\nTesting Health Check...")
    
    response = requests.get(f"{BASE_URL}/health/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    print("🚀 Django Authentication API Test")
    print("=" * 40)
    
    # Test health check first
    test_health()
    
    # Test signup
    token = test_signup()
    
    if token:
        # Test profile with token
        test_profile(token)
        
        # Test login
        login_token = test_login()
        if login_token:
            test_profile(login_token)
    
    # Test social login
    social_token = test_social_login()
    if social_token:
        test_profile(social_token)
    
    print("\n✅ Testing completed!")
    print("\nTo run the Django server:")
    print("python manage.py runserver")
