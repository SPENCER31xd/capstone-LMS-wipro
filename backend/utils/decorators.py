from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User, UserRole

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        if not user.is_active():
            return jsonify({'error': 'Account is blocked'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def active_user_required(f):
    """Decorator to require active user"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.is_active():
            return jsonify({'error': 'Account is blocked'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def get_current_user():
    """Get current authenticated user"""
    current_user_id = get_jwt_identity()
    if current_user_id:
        return User.query.get(current_user_id)
    return None
