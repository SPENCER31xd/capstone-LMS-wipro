import pytest
from app import create_app
from extensions import db
from config import TestConfig
from models.user import User, UserRole, UserStatus
from models.book import Book

@pytest.fixture
def app():
    """Create and configure a test app"""
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a test runner"""
    return app.test_cli_runner()

@pytest.fixture
def admin_user(app):
    """Create a test admin user"""
    user = User(
        name='Test Admin',
        email='admin@test.com',
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE
    )
    user.set_password('testpassword')
    
    with app.app_context():
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user

@pytest.fixture
def member_user(app):
    """Create a test member user"""
    user = User(
        name='Test Member',
        email='member@test.com',
        role=UserRole.MEMBER,
        status=UserStatus.ACTIVE
    )
    user.set_password('testpassword')
    
    with app.app_context():
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user

@pytest.fixture
def sample_book(app):
    """Create a sample book"""
    book = Book(
        title='Test Book',
        author='Test Author',
        category='Fiction',
        total_copies=3,
        available_copies=3
    )
    
    with app.app_context():
        db.session.add(book)
        db.session.commit()
        db.session.refresh(book)
        return book

@pytest.fixture
def admin_headers(client, admin_user):
    """Get authorization headers for admin user"""
    response = client.post('/auth/login', json={
        'email': 'admin@test.com',
        'password': 'testpassword'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    token = data['data']['access_token']
    
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def member_headers(client, member_user):
    """Get authorization headers for member user"""
    response = client.post('/auth/login', json={
        'email': 'member@test.com',
        'password': 'testpassword'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    token = data['data']['access_token']
    
    return {'Authorization': f'Bearer {token}'}
