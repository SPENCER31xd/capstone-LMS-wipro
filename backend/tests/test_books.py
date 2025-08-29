import pytest
from models.book import Book

class TestBookRoutes:
    """Test book management routes"""
    
    def test_get_books(self, client, member_headers, sample_book):
        """Test getting all books"""
        response = client.get('/books', headers=member_headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        
        assert response_data['status'] == 'success'
        assert len(response_data['data']) >= 1
        
        book_data = response_data['data'][0]
        assert book_data['title'] == 'Test Book'
        assert book_data['author'] == 'Test Author'
    
    def test_get_books_unauthorized(self, client, sample_book):
        """Test getting books without authentication"""
        response = client.get('/books')
        
        assert response.status_code == 401
    
    def test_get_book_by_id(self, client, member_headers, sample_book):
        """Test getting a specific book by ID"""
        response = client.get(f'/books/{sample_book.id}', headers=member_headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        
        assert response_data['status'] == 'success'
        assert response_data['data']['id'] == sample_book.id
        assert response_data['data']['title'] == 'Test Book'
    
    def test_get_book_not_found(self, client, member_headers):
        """Test getting non-existent book"""
        response = client.get('/books/999', headers=member_headers)
        
        assert response.status_code == 404
        response_data = response.get_json()
        assert response_data['status'] == 'error'
        assert 'not found' in response_data['message']
    
    def test_create_book_admin(self, client, admin_headers):
        """Test creating a book as admin"""
        data = {
            'title': 'New Test Book',
            'author': 'New Author',
            'category': 'Science',
            'total_copies': 5
        }
        
        response = client.post('/books', json=data, headers=admin_headers)
        
        assert response.status_code == 201
        response_data = response.get_json()
        
        assert response_data['status'] == 'success'
        assert response_data['message'] == 'Book created successfully'
        assert response_data['data']['title'] == 'New Test Book'
        assert response_data['data']['available_copies'] == 5
    
    def test_create_book_member_forbidden(self, client, member_headers):
        """Test creating a book as member (should be forbidden)"""
        data = {
            'title': 'Member Book',
            'author': 'Member Author',
            'category': 'Fiction',
            'total_copies': 3
        }
        
        response = client.post('/books', json=data, headers=member_headers)
        
        assert response.status_code == 403
        response_data = response.get_json()
        assert response_data['status'] == 'error'
        assert 'Admin access required' in response_data['message']
    
    def test_create_duplicate_book(self, client, admin_headers, sample_book):
        """Test creating a duplicate book"""
        data = {
            'title': 'Test Book',  # Same as sample_book
            'author': 'Test Author',  # Same as sample_book
            'category': 'Fiction',
            'total_copies': 2
        }
        
        response = client.post('/books', json=data, headers=admin_headers)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert response_data['status'] == 'error'
        assert 'already exists' in response_data['message']
    
    def test_create_book_invalid_data(self, client, admin_headers):
        """Test creating book with invalid data"""
        data = {
            'title': '',  # Empty title
            'author': 'Test Author',
            'category': 'Fiction',
            'total_copies': -1  # Invalid number
        }
        
        response = client.post('/books', json=data, headers=admin_headers)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert response_data['status'] == 'error'
        assert 'Validation failed' in response_data['message']
    
    def test_update_book_admin(self, client, admin_headers, sample_book):
        """Test updating a book as admin"""
        data = {
            'title': 'Updated Test Book',
            'category': 'Updated Category',
            'total_copies': 5
        }
        
        response = client.put(f'/books/{sample_book.id}', json=data, headers=admin_headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        
        assert response_data['status'] == 'success'
        assert response_data['message'] == 'Book updated successfully'
        assert response_data['data']['title'] == 'Updated Test Book'
        assert response_data['data']['category'] == 'Updated Category'
        assert response_data['data']['total_copies'] == 5
    
    def test_update_book_member_forbidden(self, client, member_headers, sample_book):
        """Test updating a book as member (should be forbidden)"""
        data = {
            'title': 'Member Updated Book'
        }
        
        response = client.put(f'/books/{sample_book.id}', json=data, headers=member_headers)
        
        assert response.status_code == 403
        response_data = response.get_json()
        assert response_data['status'] == 'error'
        assert 'Admin access required' in response_data['message']
    
    def test_update_nonexistent_book(self, client, admin_headers):
        """Test updating non-existent book"""
        data = {
            'title': 'Updated Title'
        }
        
        response = client.put('/books/999', json=data, headers=admin_headers)
        
        assert response.status_code == 404
        response_data = response.get_json()
        assert response_data['status'] == 'error'
        assert 'not found' in response_data['message']
    
    def test_delete_book_admin(self, client, admin_headers, sample_book):
        """Test deleting a book as admin"""
        response = client.delete(f'/books/{sample_book.id}', headers=admin_headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        
        assert response_data['status'] == 'success'
        assert response_data['message'] == 'Book deleted successfully'
    
    def test_delete_book_member_forbidden(self, client, member_headers, sample_book):
        """Test deleting a book as member (should be forbidden)"""
        response = client.delete(f'/books/{sample_book.id}', headers=member_headers)
        
        assert response.status_code == 403
        response_data = response.get_json()
        assert response_data['status'] == 'error'
        assert 'Admin access required' in response_data['message']
    
    def test_delete_nonexistent_book(self, client, admin_headers):
        """Test deleting non-existent book"""
        response = client.delete('/books/999', headers=admin_headers)
        
        assert response.status_code == 404
        response_data = response.get_json()
        assert response_data['status'] == 'error'
        assert 'not found' in response_data['message']
    
    def test_get_categories(self, client, member_headers, sample_book):
        """Test getting book categories"""
        response = client.get('/books/categories', headers=member_headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        
        assert response_data['status'] == 'success'
        assert 'Fiction' in response_data['data']
    
    def test_search_books(self, client, member_headers, sample_book):
        """Test searching books"""
        # Search by title
        response = client.get('/books?title=Test', headers=member_headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert len(response_data['data']) >= 1
        
        # Search by author
        response = client.get('/books?author=Author', headers=member_headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert len(response_data['data']) >= 1
        
        # Search available only
        response = client.get('/books?available_only=true', headers=member_headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        
        for book in response_data['data']:
            assert book['available_copies'] > 0
