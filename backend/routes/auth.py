from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import ValidationError
from extensions import db
from models.user import User, UserRole
from schemas.user_schema import UserRegistrationSchema, UserLoginSchema, UserResponseSchema
from utils.helpers import success_response, error_response

auth_bp = Blueprint('auth', __name__)

# Initialize schemas
user_registration_schema = UserRegistrationSchema()
user_login_schema = UserLoginSchema()
user_response_schema = UserResponseSchema()

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """User registration endpoint"""
    try:
        # Validate request data
        data = user_registration_schema.load(request.json)
    except ValidationError as err:
        return error_response("Validation failed", 400, err.messages)
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return error_response("User with this email already exists", 400)
    
    # Create new user
    user = User(
        name=data['name'],
        email=data['email'],
        role=UserRole.ADMIN if data['role'] == 'admin' else UserRole.MEMBER
    )
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return {
            'success': True,
            'token': access_token,
            'user': user.to_auth_dict()
        }, 201
        
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to create user", 500)

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        # Validate request data
        data = user_login_schema.load(request.json)
    except ValidationError as err:
        return error_response("Validation failed", 400, err.messages)
    
    # Find user
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return error_response("Invalid email or password", 401)
    
    if not user.is_active():
        return error_response("Account is blocked", 403)
    
    # Create access token
    access_token = create_access_token(identity=user.id)
    
    return {
        'success': True,
        'token': access_token,
        'user': user.to_auth_dict()
    }

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return error_response("User not found", 404)
    
    return success_response(user_response_schema.dump(user))

@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify JWT token"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return error_response("User not found", 404)
    
    if not user.is_active():
        return error_response("Account is blocked", 403)
    
    return success_response({
        'user': user_response_schema.dump(user),
        'valid': True
    }, "Token is valid")
