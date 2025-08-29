from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum
from datetime import datetime

class UserRole(Enum):
    ADMIN = "admin"
    MEMBER = "member"

class UserStatus(Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.MEMBER)
    status = db.Column(db.Enum(UserStatus), nullable=False, default=UserStatus.ACTIVE)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == UserRole.ADMIN
    
    def is_active(self):
        """Check if user is active"""
        return self.status == UserStatus.ACTIVE
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role.value,
            'status': self.status.value
        }
    
    def to_auth_dict(self):
        """Convert user to dictionary for authentication responses"""
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role.value
        }
    
    def __repr__(self):
        return f'<User {self.name}>'
