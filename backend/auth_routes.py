# Authentication endpoints
from flask import request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from datetime import datetime

def add_auth_routes(app):
    """Add authentication routes to the Flask app"""
    
    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        conn = sqlite3.connect('library.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user_row = cursor.fetchone()
        conn.close()
        
        if not user_row or not check_password_hash(user_row['password'], password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user_row['isActive']:
            return jsonify({'error': 'Account is inactive'}), 403
        
        # Create user object matching frontend expectations
        user = {
            'id': str(user_row['id']),
            'email': user_row['email'],
            'password': password,  # Frontend expects this for compatibility
            'firstName': user_row['firstName'],
            'lastName': user_row['lastName'],
            'role': user_row['role'],
            'createdAt': user_row['createdAt'],
            'isActive': bool(user_row['isActive'])
        }
        
        # Create JWT token
        token = create_access_token(identity=user_row['id'])
        
        return jsonify({
            'user': user,
            'token': token
        })

    @app.route('/api/signup', methods=['POST'])
    def signup():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        firstName = data.get('firstName')
        lastName = data.get('lastName')
        role = data.get('role', 'member')
        
        if not all([email, password, firstName, lastName]):
            return jsonify({'error': 'All fields are required'}), 400
        
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'User with this email already exists'}), 400
        
        # Create new user
        password_hash = generate_password_hash(password)
        cursor.execute('''
            INSERT INTO users (email, password, firstName, lastName, role, isActive)
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (email, password_hash, firstName, lastName, role))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Create user object matching frontend expectations
        user = {
            'id': str(user_id),
            'email': email,
            'password': password,  # Frontend expects this for compatibility
            'firstName': firstName,
            'lastName': lastName,
            'role': role,
            'createdAt': datetime.now().isoformat(),
            'isActive': True
        }
        
        # Create JWT token
        token = create_access_token(identity=user_id)
        
        return jsonify({
            'user': user,
            'token': token
        })


