#!/usr/bin/env python3
"""
Simple script to run the Flask backend for the Library Management System
This script ensures the database is set up and starts the Flask server
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("📦 Installing Python packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_flask.txt"])
        print("✅ Packages installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Failed to install packages. Please run: pip install -r requirements_flask.txt")
        return False
    return True

def run_flask_app():
    """Run the Flask application"""
    print("\n🚀 Starting Flask backend server...")
    try:
        # Import and run the Flask app
        from app import app
        app.run(debug=True, port=5000, host='0.0.0.0')
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed.")
        return False
    except Exception as e:
        print(f"❌ Error starting Flask app: {e}")
        return False

def main():
    print("=" * 60)
    print("🏛️  Library Management System - Flask Backend")
    print("=" * 60)
    
    # Check if requirements file exists
    if not os.path.exists('requirements_flask.txt'):
        print("❌ requirements_flask.txt not found!")
        return
    
    # Install requirements
    if not install_requirements():
        return
    
    # Run the Flask app
    run_flask_app()

if __name__ == '__main__':
    main()


