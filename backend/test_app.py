import pytest
import tempfile
import os
import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import app, init_db, seed_data


@pytest.fixture
def client():
    """Create a test client with a temporary database"""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    
    # Configure the app for testing
    app.config['TESTING'] = True
    app.config['DATABASE'] = db_path
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    # Initialize the test database
    with app.app_context():
        # Override the DATABASE variable in the app module
        import app as app_module
        app_module.DATABASE = db_path
        init_db()
        seed_data()
    
    # Create test client
    with app.test_client() as client:
        yield client
    
    # Cleanup: close and remove temporary database
    try:
        os.close(db_fd)
        # Force close any remaining connections
        import app as app_module
        app_module.DATABASE = db_path
        # Wait a bit for connections to close
        import time
        time.sleep(0.1)
        os.unlink(db_path)
    except (OSError, PermissionError):
        # On Windows, sometimes we can't delete the file immediately
        # This is not critical for test functionality
        pass


@pytest.fixture
def auth_token(client):
    """Get an authentication token for testing protected endpoints"""
    # Login to get a token
    response = client.post('/api/login', json={
        'email': 'user1@test.com',
        'password': 'password123'
    })
    
    if response.status_code == 200:
        data = response.get_json()
        return data.get('token')
    else:
        # If the default user doesn't exist, create one
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        
        # Create test user
        cursor.execute('''
            INSERT INTO users (email, password, firstName, lastName, role, isActive)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('user1@test.com', generate_password_hash('password123'), 'Test', 'User', 'member', 1))
        
        conn.commit()
        conn.close()
        
        # Try login again
        response = client.post('/api/login', json={
            'email': 'user1@test.com',
            'password': 'password123'
        })
        data = response.get_json()
        return data.get('token')


@pytest.fixture
def test_book_id(client):
    """Get a test book ID for borrowing tests"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    # Check if book with ID 3 exists, if not create it
    cursor.execute("SELECT id FROM books WHERE id = 3")
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO books (title, author, isbn, category, publishedYear, description, totalCopies, availableCopies, imageUrl)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('Test Book', 'Test Author', '1234567890', 'Fiction', 2023, 'A test book', 2, 2, 'test.jpg'))
        
        # Update the ID to 3 if it's not already 3
        if cursor.lastrowid != 3:
            cursor.execute("UPDATE books SET id = 3 WHERE id = ?", (cursor.lastrowid,))
    
    conn.commit()
    conn.close()
    return 3


class TestLoginEndpoint:
    """Test cases for the /api/login endpoint"""
    
    def test_login_success(self, client):
        """Test successful login with valid credentials"""
        # First ensure the test user exists
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        
        # Check if user exists, if not create it
        cursor.execute("SELECT id FROM users WHERE email = ?", ('user1@test.com',))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO users (email, password, firstName, lastName, role, isActive)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('user1@test.com', generate_password_hash('password123'), 'Test', 'User', 'member', 1))
            conn.commit()
        
        conn.close()
        
        # Test login
        response = client.post('/api/login', json={
            'email': 'user1@test.com',
            'password': 'password123'
        })
        
        # Assertions
        assert response.status_code == 200
        data = response.get_json()
        assert 'user' in data
        assert 'token' in data
        assert data['user']['email'] == 'user1@test.com'
        assert data['user']['firstName'] == 'Test'
        assert data['user']['lastName'] == 'User'
        assert data['user']['role'] == 'member'
        assert data['user']['isActive'] is True
    
    def test_login_failure_wrong_password(self, client):
        """Test login failure with wrong password"""
        # First ensure the test user exists
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE email = ?", ('user1@test.com',))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO users (email, password, firstName, lastName, role, isActive)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('user1@test.com', generate_password_hash('password123'), 'Test', 'User', 'member', 1))
            conn.commit()
        
        conn.close()
        
        # Test login with wrong password
        response = client.post('/api/login', json={
            'email': 'user1@test.com',
            'password': 'wrongpassword'
        })
        
        # Assertions
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'Invalid email or password'
    
    def test_login_failure_missing_fields(self, client):
        """Test login failure with missing email or password"""
        # Test missing email
        response = client.post('/api/login', json={
            'password': 'password123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'Email and password are required'
        
        # Test missing password
        response = client.post('/api/login', json={
            'email': 'user1@test.com'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'Email and password are required'
        
        # Test empty JSON
        response = client.post('/api/login', json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'Email and password are required'


class TestBorrowBookEndpoint:
    """Test cases for the /api/borrow/<book_id> endpoint"""
    
    def test_borrow_book_success(self, client, auth_token, test_book_id):
        """Test successful book borrowing"""
        # Ensure the book is available
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        cursor.execute("UPDATE books SET availableCopies = 2 WHERE id = ?", (test_book_id,))
        conn.commit()
        conn.close()
        
        # Test borrowing
        response = client.post(f'/api/borrow/{test_book_id}', 
                             headers={'Authorization': f'Bearer {auth_token}'},
                             json={'dueDate': (datetime.now() + timedelta(days=14)).isoformat()})
        
        # Assertions
        assert response.status_code == 201
        data = response.get_json()
        assert data['bookId'] == test_book_id
        assert data['type'] == 'issue'
        assert data['status'] == 'active'
        assert 'issueDate' in data
        assert 'dueDate' in data
        
        # Verify book availability was updated
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        cursor.execute("SELECT availableCopies FROM books WHERE id = ?", (test_book_id,))
        available_copies = cursor.fetchone()[0]
        conn.close()
        
        assert available_copies == 1  # Should be reduced by 1
    
    def test_borrow_book_already_borrowed(self, client, auth_token, test_book_id):
        """Test borrowing a book that's already borrowed by the same user"""
        # First borrow the book
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        
        # Ensure book is available
        cursor.execute("UPDATE books SET availableCopies = 2 WHERE id = ?", (test_book_id,))
        
        # Create a transaction record to simulate already borrowed
        # Get the user ID from the auth token
        import jwt
        decoded_token = jwt.decode(auth_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded_token['sub']
        
        cursor.execute('''
            INSERT INTO transactions (bookId, userId, type, issueDate, dueDate, status)
            VALUES (?, ?, 'issue', ?, ?, 'active')
        ''', (test_book_id, user_id, datetime.now(), datetime.now() + timedelta(days=14)))
        
        conn.commit()
        conn.close()
        
        # Try to borrow the same book again
        response = client.post(f'/api/borrow/{test_book_id}', 
                             headers={'Authorization': f'Bearer {auth_token}'},
                             json={'dueDate': (datetime.now() + timedelta(days=14)).isoformat()})
        
        # Assertions
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'User already has this book'
    
    def test_borrow_book_not_available(self, client, auth_token, test_book_id):
        """Test borrowing a book with no available copies"""
        # Set available copies to 0
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        cursor.execute("UPDATE books SET availableCopies = 0 WHERE id = ?", (test_book_id,))
        conn.commit()
        conn.close()
        
        # Try to borrow the book
        response = client.post(f'/api/borrow/{test_book_id}', 
                             headers={'Authorization': f'Bearer {auth_token}'},
                             json={'dueDate': (datetime.now() + timedelta(days=14)).isoformat()})
        
        # Assertions
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'Book not available'
    
    def test_borrow_book_not_found(self, client, auth_token):
        """Test borrowing a non-existent book"""
        response = client.post('/api/borrow/99999', 
                             headers={'Authorization': f'Bearer {auth_token}'},
                             json={'dueDate': (datetime.now() + timedelta(days=14)).isoformat()})
        
        # Assertions
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'Book not found'
    
    def test_borrow_book_unauthorized(self, client, test_book_id):
        """Test borrowing a book without authentication"""
        response = client.post(f'/api/borrow/{test_book_id}', 
                             json={'dueDate': (datetime.now() + timedelta(days=14)).isoformat()})
        
        # Assertions
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
        # The error message can be either "Authentication required" or "Missing Authorization Header"
        assert 'Authentication' in data['error'] or 'Authorization' in data['error']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
