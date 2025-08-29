#!/usr/bin/env python3
"""
JWT Authentication Test Script
This script tests the JWT authentication flow for the Library Management System
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000/api"
HEADERS = {
    "Content-Type": "application/json",
    "Origin": "http://localhost:4200"
}

def test_login():
    """Test login endpoint"""
    print("🔐 Testing Login...")
    
    login_data = {
        "email": "admin@library.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data, headers=HEADERS)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            user = data.get('user')
            
            print("✅ Login successful!")
            print(f"User: {user['firstName']} {user['lastName']} ({user['role']})")
            print(f"Token: {token[:50]}...")
            
            return token
        else:
            print(f"❌ Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return None

def test_members_without_token():
    """Test members endpoint without token"""
    print("\n🚫 Testing Members Endpoint (No Token)...")
    
    try:
        response = requests.get(f"{BASE_URL}/members", headers=HEADERS)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Correctly rejected without token")
        else:
            print(f"❌ Unexpected response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_members_with_token(token):
    """Test members endpoint with valid token"""
    print("\n🔑 Testing Members Endpoint (With Token)...")
    
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.get(f"{BASE_URL}/members", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully retrieved {len(data)} members")
            
            for member in data:
                print(f"  - {member['firstName']} {member['lastName']} ({member['email']}) - Active: {member['isActive']}")
                
        elif response.status_code == 401:
            print("❌ Authentication failed")
            print(f"Response: {response.text}")
        elif response.status_code == 403:
            print("❌ Access denied (not admin)")
            print(f"Response: {response.text}")
        else:
            print(f"❌ Unexpected response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_invalid_token():
    """Test members endpoint with invalid token"""
    print("\n🚫 Testing Members Endpoint (Invalid Token)...")
    
    headers = HEADERS.copy()
    headers["Authorization"] = "Bearer invalid_token_here"
    
    try:
        response = requests.get(f"{BASE_URL}/members", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Correctly rejected invalid token")
        else:
            print(f"❌ Unexpected response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main test function"""
    print("=" * 60)
    print("JWT Authentication Test for Library Management System")
    print("=" * 60)
    
    # Test 1: Login
    token = test_login()
    
    if not token:
        print("\n❌ Cannot proceed without valid token")
        return
    
    # Test 2: Members without token
    test_members_without_token()
    
    # Test 3: Members with valid token
    test_members_with_token(token)
    
    # Test 4: Members with invalid token
    test_invalid_token()
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()

