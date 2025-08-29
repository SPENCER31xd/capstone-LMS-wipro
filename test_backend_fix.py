#!/usr/bin/env python3
"""
Test script to verify the backend API endpoints are working after fixes
"""

import requests
import json

# Base URL for the backend
import os
BASE_URL = os.getenv('BACKEND_URL', "http://localhost:5000/api")

def test_api_endpoint(endpoint, method="GET", data=None, headers=None):
    """Test a single API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        print(f"✅ {method} {endpoint}: {response.status_code}")
        
        if response.status_code == 200 or response.status_code == 201:
            try:
                result = response.json()
                if isinstance(result, list):
                    print(f"   Response: {len(result)} items")
                    if len(result) > 0:
                        print(f"   First item keys: {list(result[0].keys()) if isinstance(result[0], dict) else 'Not a dict'}")
                else:
                    print(f"   Response: {type(result).__name__}")
                    if isinstance(result, dict):
                        print(f"   Response keys: {list(result.keys())}")
            except Exception as e:
                print(f"   Response parsing error: {e}")
                print(f"   Raw response: {response.text[:200]}...")
        else:
            print(f"   Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {method} {endpoint}: Connection failed - Is the backend running on port 5000?")
    except Exception as e:
        print(f"❌ {method} {endpoint}: {str(e)}")

def main():
    """Test all the required API endpoints"""
    print("Testing Backend API Endpoints After Fixes")
    print("=" * 60)
    
    # Test endpoints that don't require authentication
    print("\n1. Testing endpoints without authentication:")
    test_api_endpoint("/books")
    test_api_endpoint("/members")
    test_api_endpoint("/transactions")
    
    # Test with a dummy token (should fail with 401)
    print("\n2. Testing endpoints with invalid token:")
    headers = {"Authorization": "Bearer invalid_token"}
    test_api_endpoint("/books", headers=headers)
    test_api_endpoint("/members", headers=headers)
    test_api_endpoint("/transactions", headers=headers)
    
    print("\n" + "=" * 60)
    print("API Testing Complete!")
    print("\nExpected Results:")
    print("- Endpoints without auth: Should return 401 (Authentication required)")
    print("- Endpoints with invalid token: Should return 401 (Authentication required)")
    print("\nIf you see 500 errors, check the backend console for Python errors")
    print("\nTo test authenticated endpoints:")
    print("1. Start the backend server")
    print("2. Login through the Angular frontend")
    print("3. Check the browser console for successful API calls")

if __name__ == "__main__":
    main()
