#!/usr/bin/env python3
"""
Comprehensive test script to verify all backend API endpoints are working after fixes
"""

import requests
import json
import time

# Base URL for the backend - can be overridden by environment variable
import os
BASE_URL = os.getenv('BACKEND_URL', "http://localhost:5000/api")

def test_api_endpoint(endpoint, method="GET", data=None, headers=None, expected_status=None):
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
        
        status_ok = "✅" if response.status_code == expected_status else "⚠️"
        print(f"{status_ok} {method} {endpoint}: {response.status_code}")
        
        if expected_status and response.status_code != expected_status:
            print(f"   ⚠️  Expected {expected_status}, got {response.status_code}")
        
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
        print(f"❌ {method} {endpoint}: Connection failed - Is the backend running? Check the URL: {BASE_URL}")
    except Exception as e:
        print(f"❌ {method} {endpoint}: {str(e)}")

def main():
    """Test all the required API endpoints"""
    print("Comprehensive Backend API Testing After Fixes")
    print("=" * 70)
    
    # Test endpoints that don't require authentication
    print("\n1. Testing endpoints without authentication (should return 401):")
    test_api_endpoint("/books", expected_status=401)
    test_api_endpoint("/members", expected_status=401)
    test_api_endpoint("/transactions", expected_status=401)
    
    # Test with a dummy token (should fail with 401)
    print("\n2. Testing endpoints with invalid token (should return 401):")
    headers = {"Authorization": "Bearer invalid_token"}
    test_api_endpoint("/books", headers=headers, expected_status=401)
    test_api_endpoint("/members", headers=headers, expected_status=401)
    test_api_endpoint("/transactions", headers=headers, expected_status=401)
    
    # Test book-specific endpoints
    print("\n3. Testing book-specific endpoints with invalid token:")
    test_api_endpoint("/books/1", headers=headers, expected_status=401)
    test_api_endpoint("/books/1", method="PUT", headers=headers, data={"title": "Test"}, expected_status=401)
    test_api_endpoint("/books/1", method="DELETE", headers=headers, expected_status=401)
    
    # Test transaction endpoints
    print("\n4. Testing transaction endpoints with invalid token:")
    test_api_endpoint("/borrow/1", method="POST", headers=headers, data={"dueDate": "2025-12-31"}, expected_status=401)
    test_api_endpoint("/return/1", method="POST", headers=headers, data={"returnDate": "2025-01-01"}, expected_status=401)
    
    print("\n" + "=" * 70)
    print("Comprehensive API Testing Complete!")
    print("\nExpected Results:")
    print("- All endpoints should return 401 (Authentication required)")
    print("- No more 500 Internal Server errors")
    print("- No more 'TypeError: tuple indices must be integers or slices, not str'")
    print("\nIf you see 500 errors, check the backend console for Python errors")
    print("\nTo test authenticated endpoints:")
    print("1. Start the backend server")
    print("2. Login through the Angular frontend")
    print("3. Check the browser console for successful API calls")
    print("4. Verify that member dashboard shows 'My Books' data")
    print("5. Verify that admin dashboard shows correct member counts")
    print("6. Test Add/Update Book functionality")

if __name__ == "__main__":
    main()




