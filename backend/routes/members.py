from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError
from extensions import db
from models.user import User, UserRole, UserStatus
from models.transaction import Transaction
from schemas.user_schema import UserResponseSchema, UserUpdateSchema
from utils.decorators import admin_required, active_user_required
from utils.helpers import success_response, error_response

members_bp = Blueprint('members', __name__)

# Initialize schemas
user_response_schema = UserResponseSchema()
user_update_schema = UserUpdateSchema()

@members_bp.route('', methods=['GET'])
@admin_required
def get_all_members():
    """Get all members (admin only)"""
    # Get query parameters
    role_filter = request.args.get('role', '').lower()
    status_filter = request.args.get('status', '').lower()
    search = request.args.get('search', '').strip()
    
    # Build query
    query = User.query
    
    # Filter by role if specified
    if role_filter == 'admin':
        query = query.filter(User.role == UserRole.ADMIN)
    elif role_filter == 'member':
        query = query.filter(User.role == UserRole.MEMBER)
    
    # Filter by status if specified
    if status_filter == 'active':
        query = query.filter(User.status == UserStatus.ACTIVE)
    elif status_filter == 'blocked':
        query = query.filter(User.status == UserStatus.BLOCKED)
    
    # Search by name or email
    if search:
        query = query.filter(
            (User.name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%"))
        )
    
    users = query.order_by(User.created_at.desc()).all()
    
    # Add transaction statistics for each user
    users_data = []
    for user in users:
        user_dict = user_response_schema.dump(user)
        
        # Get transaction statistics
        total_transactions = Transaction.query.filter_by(user_id=user.id).count()
        active_transactions = Transaction.query.filter_by(
            user_id=user.id, 
            status='issued'
        ).count()
        overdue_transactions = Transaction.query.filter_by(user_id=user.id).filter(
            Transaction.due_date < db.func.current_timestamp(),
            Transaction.status == 'issued'
        ).count()
        
        user_dict.update({
            'total_transactions': total_transactions,
            'active_transactions': active_transactions,
            'overdue_transactions': overdue_transactions
        })
        
        users_data.append(user_dict)
    
    return users_data

@members_bp.route('/<int:user_id>', methods=['GET'])
@admin_required
def get_member(user_id):
    """Get specific member details (admin only)"""
    user = User.query.get(user_id)
    
    if not user:
        return error_response("User not found", 404)
    
    user_data = user_response_schema.dump(user)
    
    # Get detailed transaction information
    transactions = Transaction.query.filter_by(user_id=user.id).all()
    user_data['transactions'] = [
        {
            'id': t.id,
            'book_title': t.book.title if t.book else 'Unknown',
            'issue_date': t.issue_date.isoformat(),
            'due_date': t.due_date.isoformat(),
            'return_date': t.return_date.isoformat() if t.return_date else None,
            'status': t.status.value,
            'days_overdue': t.days_overdue()
        }
        for t in transactions
    ]
    
    return user_data

@members_bp.route('/<int:user_id>', methods=['PUT'])
@admin_required
def update_member(user_id):
    """Update member details (admin only)"""
    user = User.query.get(user_id)
    
    if not user:
        return error_response("User not found", 404)
    
    try:
        data = user_update_schema.load(request.json)
    except ValidationError as err:
        return error_response("Validation failed", 400, err.messages)
    
    # Update user fields
    if 'name' in data:
        user.name = data['name']
    
    if 'status' in data:
        if data['status'] == 'active':
            user.status = UserStatus.ACTIVE
        elif data['status'] == 'blocked':
            user.status = UserStatus.BLOCKED
    
    try:
        db.session.commit()
        
        return user.to_dict()
        
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to update member", 500)

@members_bp.route('/<int:user_id>/block', methods=['POST'])
@admin_required
def block_member(user_id):
    """Block a member (admin only)"""
    user = User.query.get(user_id)
    
    if not user:
        return error_response("User not found", 404)
    
    if user.is_admin():
        return error_response("Cannot block admin users", 400)
    
    user.status = UserStatus.BLOCKED
    
    try:
        db.session.commit()
        return {'success': True, 'message': 'Member blocked successfully'}
        
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to block member", 500)

@members_bp.route('/<int:user_id>/unblock', methods=['POST'])
@admin_required
def unblock_member(user_id):
    """Unblock a member (admin only)"""
    user = User.query.get(user_id)
    
    if not user:
        return error_response("User not found", 404)
    
    user.status = UserStatus.ACTIVE
    
    try:
        db.session.commit()
        return {'success': True, 'message': 'Member unblocked successfully'}
        
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to unblock member", 500)

@members_bp.route('/stats', methods=['GET'])
@admin_required
def get_member_stats():
    """Get member statistics (admin only)"""
    total_members = User.query.filter(User.role == UserRole.MEMBER).count()
    active_members = User.query.filter(
        User.role == UserRole.MEMBER,
        User.status == UserStatus.ACTIVE
    ).count()
    blocked_members = User.query.filter(
        User.role == UserRole.MEMBER,
        User.status == UserStatus.BLOCKED
    ).count()
    
    # Members with active transactions
    members_with_books = db.session.query(User.id).join(Transaction).filter(
        User.role == UserRole.MEMBER,
        Transaction.status == 'issued'
    ).distinct().count()
    
    stats = {
        'total_members': total_members,
        'active_members': active_members,
        'blocked_members': blocked_members,
        'members_with_active_books': members_with_books
    }
    
    return stats
