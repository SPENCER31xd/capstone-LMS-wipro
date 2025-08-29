# Member endpoints
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request
import sqlite3

def add_member_routes(app):
    """Add member routes to the Flask app"""
    
    @app.route('/api/members', methods=['GET'])
    def get_members():
        verify_jwt_in_request()
        
        conn = sqlite3.connect('library.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE role = 'member' ORDER BY createdAt DESC")
        members_rows = cursor.fetchall()
        conn.close()
        
        members = []
        for member_row in members_rows:
            member = {
                'id': str(member_row['id']),
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

    @app.route('/api/members/<int:user_id>', methods=['PUT'])
    def update_member(user_id):
        verify_jwt_in_request()
        
        data = request.get_json()
        is_active = data.get('isActive')
        
        if is_active is None:
            return jsonify({'error': 'isActive field is required'}), 400
        
        conn = sqlite3.connect('library.db')
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
            'id': str(user_id),
            'email': member_row['email'],
            'password': '',
            'firstName': member_row['firstName'],
            'lastName': member_row['lastName'],
            'role': member_row['role'],
            'createdAt': member_row['createdAt'],
            'isActive': is_active
        }
        
        return jsonify(member)


