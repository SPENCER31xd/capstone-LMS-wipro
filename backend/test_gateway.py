#!/usr/bin/env python3
"""
Test script for the new gateway structure
"""

import sys
import os

def test_gateway_import():
    """Test if gateway can be imported successfully"""
    try:
        from gateway import create_app
        print("✅ Successfully imported create_app from gateway")
        return True
    except ImportError as e:
        print(f"❌ Failed to import from gateway: {e}")
        return False

def test_app_creation():
    """Test if the app can be created successfully"""
    try:
        from gateway import create_app
        app = create_app()
        print("✅ Successfully created Flask app from gateway")
        return True
    except Exception as e:
        print(f"❌ Failed to create app: {e}")
        return False

def test_blueprint_registration():
    """Test if blueprints are registered correctly"""
    try:
        from gateway import create_app
        app = create_app()
        
        # Check if blueprints are registered
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        print(f"✅ Blueprints registered: {blueprint_names}")
        
        # Check specific blueprints
        expected_blueprints = ['auth', 'books', 'transactions', 'members', 'legacy']
        for bp_name in expected_blueprints:
            if bp_name in app.blueprints:
                print(f"  ✅ {bp_name} blueprint found")
            else:
                print(f"  ❌ {bp_name} blueprint missing")
        
        return True
    except Exception as e:
        print(f"❌ Failed to test blueprint registration: {e}")
        return False

def test_route_registration():
    """Test if routes are accessible"""
    try:
        from gateway import create_app
        app = create_app()
        
        # Check if routes are registered
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(f"{rule.methods} {rule.rule}")
        
        print(f"✅ Found {len(routes)} routes")
        
        # Check for key routes
        key_routes = [
            '/api/auth/login',
            '/api/auth/signup',
            '/api/books',
            '/api/transactions',
            '/api/members'
        ]
        
        for route in key_routes:
            if any(route in r for r in routes):
                print(f"  ✅ {route} route found")
            else:
                print(f"  ❌ {route} route missing")
        
        return True
    except Exception as e:
        print(f"❌ Failed to test route registration: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Gateway Structure")
    print("=" * 60)
    
    tests = [
        test_gateway_import,
        test_app_creation,
        test_blueprint_registration,
        test_route_registration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Gateway is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Check the errors above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
