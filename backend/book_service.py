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
    return jsonify({'status': 'healthy', 'service': 'book-service'})

# Book API Routes
@app.route('/books', methods=['GET'])
def get_books():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM books ORDER BY createdAt DESC")
    books_rows = cursor.fetchall()
    conn.close()

    books = []
    for book_row in books_rows:
        book = {
            'id': str(book_row['id']),  # Convert to string for Angular
            'title': book_row['title'],
            'author': book_row['author'],
            'isbn': book_row['isbn'] or '',
            'category': book_row['category'],
            'publishedYear': book_row['publishedYear'],
            'description': book_row['description'] or '',
            'totalCopies': book_row['totalCopies'],
            'availableCopies': book_row['availableCopies'],
            'imageUrl': book_row['imageUrl'],
            'createdAt': book_row['createdAt'],
            'updatedAt': book_row['updatedAt']
        }
        books.append(book)

    return jsonify(books)

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    book_row = cursor.fetchone()
    conn.close()

    if not book_row:
        return jsonify({'error': 'Book not found'}), 404

    book = {
        'id': str(book_row['id']),
        'title': book_row['title'],
        'author': book_row['author'],
        'isbn': book_row['isbn'] or '',
        'category': book_row['category'],
        'publishedYear': book_row['publishedYear'],
        'description': book_row['description'] or '',
        'totalCopies': book_row['totalCopies'],
        'availableCopies': book_row['availableCopies'],
        'imageUrl': book_row['imageUrl'],
        'createdAt': book_row['createdAt'],
        'updatedAt': book_row['updatedAt']
    }

    return jsonify(book)

@app.route('/books', methods=['POST'])
@admin_required
def create_book():
    data = request.get_json()
    title = data.get('title')
    author = data.get('author')
    isbn = data.get('isbn', '')
    category = data.get('category')
    publishedYear = data.get('publishedYear')
    description = data.get('description', '')
    totalCopies = data.get('totalCopies')
    imageUrl = data.get('imageUrl', 'https://via.placeholder.com/150x200')

    if not all([title, author, category, publishedYear, totalCopies]):
        return jsonify({'error': 'Required fields missing'}), 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO books (title, author, isbn, category, publishedYear, description, totalCopies, availableCopies, imageUrl, updatedAt)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, author, isbn, category, publishedYear, description, totalCopies, totalCopies, imageUrl, datetime.now()))

    book_id = cursor.lastrowid
    conn.commit()
    conn.close()

    book = {
        'id': int(book_id),
        'title': title,
        'author': author,
        'isbn': isbn or '',
        'category': category,
        'publishedYear': publishedYear,
        'description': description or '',
        'totalCopies': totalCopies,
        'availableCopies': totalCopies,
        'imageUrl': imageUrl,
        'createdAt': datetime.now().isoformat(),
        'updatedAt': datetime.now().isoformat()
    }

    return jsonify(book), 201

@app.route('/books/<int:book_id>', methods=['PUT'])
@admin_required
def update_book(book_id):
    data = request.get_json()

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get current book
    cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    book_row = cursor.fetchone()

    if not book_row:
        conn.close()
        return jsonify({'error': 'Book not found'}), 404

    # Update fields
    title = data.get('title', book_row['title'])
    author = data.get('author', book_row['author'])
    isbn = data.get('isbn', book_row['isbn'])
    category = data.get('category', book_row['category'])
    publishedYear = data.get('publishedYear', book_row['publishedYear'])
    description = data.get('description', book_row['description'])
    imageUrl = data.get('imageUrl', book_row['imageUrl'])

    # Handle totalCopies change
    totalCopies = data.get('totalCopies', book_row['totalCopies'])
    if totalCopies != book_row['totalCopies']:
        difference = totalCopies - book_row['totalCopies']
        availableCopies = max(0, book_row['availableCopies'] + difference)
    else:
        availableCopies = book_row['availableCopies']

    cursor.execute('''
        UPDATE books
        SET title = ?, author = ?, isbn = ?, category = ?, publishedYear = ?,
            description = ?, totalCopies = ?, availableCopies = ?, imageUrl = ?, updatedAt = ?
        WHERE id = ?
    ''', (title, author, isbn, category, publishedYear, description, totalCopies, availableCopies, imageUrl, datetime.now(), book_id))

    conn.commit()
    conn.close()

    book = {
        'id': int(book_id),
        'title': title,
        'author': author,
        'isbn': isbn or '',
        'category': category,
        'publishedYear': publishedYear,
        'description': description or '',
        'totalCopies': totalCopies,
        'availableCopies': availableCopies,
        'imageUrl': imageUrl,
        'createdAt': book_row['createdAt'],
        'updatedAt': datetime.now().isoformat()
    }

    return jsonify(book)

@app.route('/books/<int:book_id>', methods=['DELETE'])
@admin_required
def delete_book(book_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Check if book has active transactions
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE bookId = ? AND status = 'active'", (book_id,))
    active_transactions = cursor.fetchone()[0]

    if active_transactions > 0:
        conn.close()
        return jsonify({'error': 'Cannot delete book with active transactions'}), 400

    cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Book not found'}), 404

    conn.commit()
    conn.close()

    return jsonify(True)

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
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, port=port, host='0.0.0.0')

