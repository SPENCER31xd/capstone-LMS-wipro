import pytest
from models.user import User

class TestAuthRoutes:
    """Test authentication routes"""
    
    def test_signup_success(self, client):
        """Test successful user signup"""
        data = {
            'name': 'New User',
            'email': 'newuser@test.com',
            'password': 'testpassword123',
            'role': 'member'
        }
        
        response = client.post('/auth/signup', json=data)
        
        assert response.status_code == 201
        response_data = response.get_json()
        
        assert response_data['status'] == 'success'
        assert response_data['message'] == 'User registered successfully'
        assert 'access_token' in response_data['data']
        assert response_data['data']['user']['email'] == 'newuser@test.com'
        assert response_data['data']['user']['role'] == 'member'
    
    def test_signup_admin(self, client):
        """Test admin user signup"""
        data = {
            'name': 'New Admin',
            'email': 'newadmin@test.com',
            'password': 'testpassword123',
            'role': 'admin'
        }
        
        response = client.post('/auth/signup', json=data)
        
        assert response.status_code == 201
        response_data = response.get_json()
        assert response_data['data']['user']['role'] == 'admin'
    
    def test_signup_duplicate_email(self, client, member_user):
        """Test signup with duplicate email"""
        data = {
            'name': 'Another User',
            'email': 'member@test.com',  # Already exists
            'password': 'testpassword123',
            'role': 'member'
        }
        
        response = client.post('/auth/signup', json=data)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert response_data['status'] == 'error'
        assert 'already exists' in response_data['message']
    
    def test_signup_invalid_data(self, client):
        """Test signup with invalid data"""
        # Missing required fields
        data = {
            'name': 'Test User',
            'email': 'invalid-email',  # Invalid email
            'password': '123'  # Too short
        }
        
        response = client.post('/auth/signup', json=data)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert response_data['status'] == 'error'
        assert 'Validation failed' in response_data['message']
    
    def test_login_success(self, client, member_user):
        """Test successful login"""
        data = {
            'email': 'member@test.com',
            'password': 'testpassword'
        }
        
        response = client.post('/auth/login', json=data)
        
        assert response.status_code == 200
        response_data = response.get_json()
        
        assert response_data['status'] == 'success'
        assert response_data['message'] == 'Login successful'
        assert 'access_token' in response_data['data']
        assert response_data['data']['user']['email'] == 'member@test.com'
    
    def test_login_invalid_credentials(self, client, member_user):
        """Test login with invalid credentials"""
        data = {
            'email': 'member@test.com',
            'password': 'wrongpassword'
        }
        
        response = client.post('/auth/login', json=data)
        
        assert response.status_code == 401
        response_data = response.get_json()
        assert response_data['status'] == 'error'
        assert 'Invalid email or password' in response_data['message']
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        data = {
            'email': 'nonexistent@test.com',
            'password': 'testpassword'
        }
        
        response = client.post('/auth/login', json=data)
        
        assert response.status_code == 401
        response_data = response.get_json()
        assert response_data['status'] == 'error'
        assert 'Invalid email or password' in response_data['message']
    
    def test_get_profile(self, client, member_headers):
        """Test get user profile"""
        response = client.get('/auth/profile', headers=member_headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        
        assert response_data['status'] == 'success'
        assert response_data['data']['email'] == 'member@test.com'
        assert response_data['data']['name'] == 'Test Member'
    
    def test_get_profile_unauthorized(self, client):
        """Test get profile without authentication"""
        response = client.get('/auth/profile')
        
        assert response.status_code == 401
    
    def test_verify_token(self, client, member_headers):
        """Test token verification"""
        response = client.get('/auth/verify', headers=member_headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        
        assert response_data['status'] == 'success'
        assert response_data['message'] == 'Token is valid'
        assert response_data['data']['valid'] is True
    
    def test_verify_token_unauthorized(self, client):
        """Test token verification without token"""
        response = client.get('/auth/verify')
        
        assert response.status_code == 401
