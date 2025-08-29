#!/usr/bin/env python3
"""
Start the corrected Flask backend with proper CORS configuration
"""

import subprocess
import os
import sys

def main():
    """Start the corrected Flask backend"""
    
    # Change to backend directory
    backend_dir = os.path.join(os.getcwd(), 'backend')
    if os.path.exists(backend_dir):
        os.chdir(backend_dir)
    
    print("🚀 Starting Library Management Backend with CORS fixes")
    print("📍 Backend Server: Running on port 5000")
    print("🔧 CORS enabled for: localhost:4200 and Docker services")
    print("📋 API endpoints:")
    print("   POST /api/login")
    print("   POST /api/signup") 
    print("   GET  /api/books")
    print("   POST /api/books")
    print("   PUT  /api/books/<id>")
    print("   DELETE /api/books/<id>")
    print("   POST /api/borrow/<book_id>    ← CORS FIXED")
    print("   POST /api/return/<transaction_id>")
    print("   GET  /api/transactions")
    print("   GET  /api/members")
    print("   PUT  /api/members/<user_id>")
    print()
    print("🔑 Default credentials:")
    print("   Admin:  admin@library.com / admin123")
    print("   Member: member@library.com / member123")
    print()
    print("✅ CORS issues should now be resolved!")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Start the corrected Flask app
    try:
        subprocess.run([sys.executable, 'corrected_app.py'], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error starting server: {e}")

if __name__ == '__main__':
    main()