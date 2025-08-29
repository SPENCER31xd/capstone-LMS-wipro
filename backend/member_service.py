from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity, jwt_required
import sqlite3
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)

# Configuration
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')

# Initialize extensions
jwt = JWTManager(app)

# Configure CORS
CORS(app, 
     origins=['http://localhost:4200', 'http://localhost:3000', 'http://frontend', 'http://localhost', 'http://gateway:5000'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
     supports_credentials=True)

# Database setup
DATABASE = os.environ.get('DATABASE_URL', 'library.db')

def admin_required(fn):
    """Decorator to require admin role for protected routes"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            
            # Check if user is admin
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM users WHERE id = ?", (current_user_id,))
            user_role = cursor.fetchone()
            conn.close()
            
            if not user_role or user_role[0] != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authentication required'}), 401
    
    return wrapper

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'member-service'})

# Member API Routes
@app.route('/members', methods=['GET'])
@admin_required
def get_members():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE role = 'member' ORDER BY createdAt DESC")
        members_rows = cursor.fetchall()
        conn.close()

        members = []
        for member_row in members_rows:
            member = {
                'id': member_row['id'],  # Keep as integer for Angular
                'email': member_row['email'],
                'password': '',  # Don't return password
                'firstName': member_row['firstName'],
                'lastName': member_row['lastName'],
                'role': member_row['role'],
                'createdAt': member_row['createdAt'],
                'isActive': bool(member_row['isActive'])
            }
            members.append(member)

        return jsonify(members)
    except Exception as e:
        return jsonify({'error': 'Failed to fetch members'}), 500

@app.route('/members/<int:user_id>', methods=['PUT'])
@admin_required
def update_member(user_id):
    try:
        data = request.get_json()
        is_active = data.get('isActive')

        if is_active is None:
            return jsonify({'error': 'isActive field is required'}), 400

        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ? AND role = 'member'", (user_id,))
        member_row = cursor.fetchone()

        if not member_row:
            conn.close()
            return jsonify({'error': 'Member not found'}), 404

        cursor.execute("UPDATE users SET isActive = ? WHERE id = ?", (is_active, user_id))
        conn.commit()
        conn.close()

        member = {
            'id': user_id,  # Keep as integer for Angular
            'email': member_row['email'],
            'password': '',
            'firstName': member_row['firstName'],
            'lastName': member_row['lastName'],
            'role': member_row['role'],
            'createdAt': member_row['createdAt'],
            'isActive': is_active
        }

        return jsonify(member)
    except Exception as e:
        return jsonify({'error': 'Failed to update member'}), 500

# Handle preflight OPTIONS requests for CORS
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify()
        origin = request.headers.get('Origin')
        if origin in ['http://localhost:4200', 'http://localhost:3000', 'http://frontend', 'http://localhost', 'http://gateway:5000']:
            response.headers.add("Access-Control-Allow-Origin", origin)
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,X-Requested-With")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
        response.headers.add('Access-Control-Allow-Credentials', "true")
        return response

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin in ['http://localhost:4200', 'http://localhost:3000', 'http://frontend', 'http://localhost', 'http://gateway:5000']:
        response.headers.add('Access-Control-Allow-Origin', origin)
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(debug=True, port=port, host='0.0.0.0')

