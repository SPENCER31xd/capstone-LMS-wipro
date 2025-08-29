#!/usr/bin/env python3
"""
Quick start script for Library Management System
This script will set up the database and run the Flask application
"""

import os
import subprocess
import sys
from gateway import create_app

def setup_database():
    """Set up the database and seed data"""
    print("Setting up database...")
    
    app = create_app()
    with app.app_context():
        # Import and create all tables
        from extensions import db
        db.create_all()
        print("Database tables created successfully!")
        
        # Check if we need to seed data
        try:
            from models.user import User
            user_count = User.query.count()
            
            if user_count == 0:
                print("Database is empty. Running seed script...")
                # Import and run seed data
                from legacy_routes import seed_data
                seed_data()
                print("Seed data added successfully!")
            else:
                print(f"Database already contains {user_count} users. Skipping seed data.")
        except Exception as e:
            print(f"Note: Using legacy database structure. Error: {e}")
            # Legacy database structure
            from legacy_routes import init_db, seed_data
            if not os.path.exists('library.db'):
                init_db()
                seed_data()
                print("Legacy database initialized with seed data!")

def main():
    """Main function to run the setup"""
    print("=" * 60)
    print("Library Management System - Backend Setup")
    print("=" * 60)
    
    # Set up database
    setup_database()
    
    print("\n" + "=" * 60)
    print("Setup completed successfully!")
    print("=" * 60)
    print("\nStarting Flask application...")
    print("API will be available on port 5000")
    print("\nDefault admin login:")
    print("  Email: admin@library.com")
    print("  Password: admin123")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    # Run the Flask application
    app = create_app()
    app.run(debug=True, port=5000, host='0.0.0.0')

if __name__ == '__main__':
    main()
