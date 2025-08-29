"""
API Gateway for Library Management System
This file serves as the main entry point and application factory
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, verify_jwt_in_request, get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import requests
from datetime import datetime, timedelta
from functools import wraps

# Database setup
DATABASE = os.environ.get('DATABASE_URL', 'library.db')

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            firstName TEXT NOT NULL,
            lastName TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'member',
            isActive BOOLEAN DEFAULT 1,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Books table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT,
            category TEXT NOT NULL,
            publishedYear INTEGER,
            description TEXT,
            totalCopies INTEGER NOT NULL,
            availableCopies INTEGER NOT NULL,
            imageUrl TEXT,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bookId INTEGER NOT NULL,
            userId INTEGER NOT NULL,
            type TEXT NOT NULL,
            issueDate TIMESTAMP NOT NULL,
            dueDate TIMESTAMP NOT NULL,
            returnDate TIMESTAMP,
            status TEXT NOT NULL,
            fine REAL DEFAULT 0,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bookId) REFERENCES books (id),
            FOREIGN KEY (userId) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()

def seed_data():
    """Seed the database with initial data"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    # Insert users
    users = [
        ('admin@library.com', generate_password_hash('admin123'), 'Admin', 'User', 'admin', 1),
        ('member@library.com', generate_password_hash('member123'), 'John', 'Doe', 'member', 1),
        ('jane@library.com', generate_password_hash('jane123'), 'Jane', 'Smith', 'member', 1)
    ]

    cursor.executemany('''
        INSERT INTO users (email, password, firstName, lastName, role, isActive)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', users)

    # Insert books including your book
    books = [
        ('The Great Gatsby', 'F. Scott Fitzgerald', '978-0-7432-7356-5', 'Fiction', 1925, 'A classic American novel set in the Jazz Age.', 5, 3, 'https://via.placeholder.com/150x200'),
        ('To Kill a Mockingbird', 'Harper Lee', '978-0-06-112008-4', 'Fiction', 1960, 'A gripping tale of racial injustice and childhood innocence.', 4, 2, 'https://via.placeholder.com/150x200'),
        ('Clean Code', 'Robert C. Martin', '978-0-13-235088-4', 'Technology', 2008, 'A handbook of agile software craftsmanship.', 6, 4, 'https://via.placeholder.com/150x200'),
        ('Sapiens', 'Yuval Noah Harari', '978-0-06-231609-7', 'History', 2011, 'A brief history of humankind.', 3, 1, 'https://via.placeholder.com/150x200'),
        ('The Lean Startup', 'Eric Ries', '978-0-307-88789-4', 'Non-Fiction', 2011, 'How constant innovation creates radically successful businesses.', 4, 3, 'https://via.placeholder.com/150x200'),
        ('Do bailo ki gatha', 'prem chand', '', 'Fiction', 1920, 'A classic Hindi literature work.', 2, 2, 'https://via.placeholder.com/150x200')
    ]

    cursor.executemany('''
        INSERT INTO books (title, author, isbn, category, publishedYear, description, totalCopies, availableCopies, imageUrl)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', books)

    # Insert sample transactions
    transactions = [
        (1, 2, 'issue', datetime.now() - timedelta(days=5), datetime.now() + timedelta(days=9), None, 'active', 0),
        (2, 3, 'issue', datetime.now() - timedelta(days=10), datetime.now() + timedelta(days=4), datetime.now() - timedelta(days=2), 'returned', 0)
    ]

    cursor.executemany('''
        INSERT INTO transactions (bookId, userId, type, issueDate, dueDate, returnDate, status, fine)
        VALUES (?, ?, 'issue', ?, ?, ?, ?, ?)
    ''', transactions)

    conn.commit()
    conn.close()

def create_app(config_class=None):
    """Application factory function"""
    app = Flask(__name__)
    
    # Load configuration
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    
    # Service URLs
    BOOK_SERVICE_URL = os.environ.get('BOOK_SERVICE_URL', 'http://book-service:5001')
    MEMBER_SERVICE_URL = os.environ.get('MEMBER_SERVICE_URL', 'http://member-service:5002')
    TRANSACTION_SERVICE_URL = os.environ.get('TRANSACTION_SERVICE_URL', 'http://transaction-service:5003')
    
    # Initialize extensions
    jwt = JWTManager(app)
    
    # Configure CORS
    CORS(app, 
         origins=['http://localhost:4200', 'http://localhost:3000', 'http://frontend', 'http://localhost'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
         supports_credentials=True)
    
    # JWT Error Handlers
    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return jsonify({'error': 'Missing Authorization Header'}), 401

    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        return jsonify({'error': 'Invalid token'}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401

    # Authentication Routes - Match Angular expectations
    @app.route('/api/login', methods=['POST'])
    def auth_login():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user_row = cursor.fetchone()
        conn.close()

        if not user_row or not check_password_hash(user_row['password'], password):
            return jsonify({'error': 'Invalid email or password'}), 401

        if not user_row['isActive']:
            return jsonify({'error': 'Account is inactive'}), 403

        # Create user object matching frontend expectations
        user = {
            'id': user_row['id'],  # Keep as integer for Angular
            'email': user_row['email'],
            'password': password,  # Frontend expects this for compatibility
            'firstName': user_row['firstName'],
            'lastName': user_row['lastName'],
            'role': user_row['role'],
            'createdAt': user_row['createdAt'],
            'isActive': bool(user_row['isActive'])
        }

        # Create JWT token
        token = create_access_token(identity=user_row['id'])

        return jsonify({
            'user': user,
            'token': token
        })

    @app.route('/api/signup', methods=['POST'])
    def auth_signup():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        firstName = data.get('firstName')
        lastName = data.get('lastName')
        role = data.get('role', 'member')

        if not all([email, password, firstName, lastName]):
            return jsonify({'error': 'All fields are required'}), 400

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'User with this email already exists'}), 400

        # Create new user
        password_hash = generate_password_hash(password)
        cursor.execute('''
            INSERT INTO users (email, password, firstName, lastName, role, isActive)
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (email, password_hash, firstName, lastName, role))

        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Create user object matching frontend expectations
        user = {
            'id': user_id,  # Keep as integer for Angular
            'email': email,
            'password': password,  # Frontend expects this for compatibility
            'firstName': firstName,
            'lastName': lastName,
            'role': role,
            'createdAt': datetime.now().isoformat(),
            'isActive': True
        }

        # Create JWT token
        token = create_access_token(identity=user_id)

        return jsonify({
            'user': user,
            'token': token
        })

    # Book API Routes - Route to book service
    @app.route('/api/books', methods=['GET'])
    def get_books():
        try:
            response = requests.get(f"{BOOK_SERVICE_URL}/books")
            return jsonify(response.json()), response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({'error': f'Book service unavailable: {str(e)}'}), 503

    @app.route('/api/books/<int:book_id>', methods=['GET'])
    def get_book(book_id):
        try:
            response = requests.get(f"{BOOK_SERVICE_URL}/books/{book_id}")
            return jsonify(response.json()), response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({'error': f'Book service unavailable: {str(e)}'}), 503

    @app.route('/api/books', methods=['POST'])
    def create_book():
        try:
            # Forward the request with headers
            headers = {'Authorization': request.headers.get('Authorization')}
            response = requests.post(f"{BOOK_SERVICE_URL}/books", 
                                  json=request.get_json(), 
                                  headers=headers)
            return jsonify(response.json()), response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({'error': f'Book service unavailable: {str(e)}'}), 503

    @app.route('/api/books/<int:book_id>', methods=['PUT'])
    def update_book(book_id):
        try:
            headers = {'Authorization': request.headers.get('Authorization')}
            response = requests.put(f"{BOOK_SERVICE_URL}/books/{book_id}", 
                                 json=request.get_json(), 
                                 headers=headers)
            return jsonify(response.json()), response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({'error': f'Book service unavailable: {str(e)}'}), 503

    @app.route('/api/books/<int:book_id>', methods=['DELETE'])
    def delete_book(book_id):
        try:
            headers = {'Authorization': request.headers.get('Authorization')}
            response = requests.delete(f"{BOOK_SERVICE_URL}/books/{book_id}", 
                                    headers=headers)
            return jsonify(response.json()), response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({'error': f'Book service unavailable: {str(e)}'}), 503

    # Transaction API Routes - Route to transaction service
    @app.route('/api/borrow/<int:book_id>', methods=['POST'])
    def borrow_book(book_id):
        try:
            headers = {'Authorization': request.headers.get('Authorization')}
            response = requests.post(f"{TRANSACTION_SERVICE_URL}/borrow/{book_id}", 
                                  json=request.get_json(), 
                                  headers=headers)
            return jsonify(response.json()), response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({'error': f'Transaction service unavailable: {str(e)}'}), 503

    @app.route('/api/return/<int:transaction_id>', methods=['POST'])
    def return_book(transaction_id):
        try:
            headers = {'Authorization': request.headers.get('Authorization')}
            response = requests.post(f"{TRANSACTION_SERVICE_URL}/return/{transaction_id}", 
                                  json=request.get_json(), 
                                  headers=headers)
            return jsonify(response.json()), response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({'error': f'Transaction service unavailable: {str(e)}'}), 503

    @app.route('/api/transactions', methods=['GET'])
    def get_transactions():
        try:
            headers = {'Authorization': request.headers.get('Authorization')}
            response = requests.get(f"{TRANSACTION_SERVICE_URL}/transactions", 
                                 headers=headers)
            return jsonify(response.json()), response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({'error': f'Transaction service unavailable: {str(e)}'}), 503

    # Member API Routes - Route to member service
    @app.route('/api/members', methods=['GET'])
    def get_members():
        try:
            headers = {'Authorization': request.headers.get('Authorization')}
            response = requests.get(f"{MEMBER_SERVICE_URL}/members", 
                                 headers=headers)
            return jsonify(response.json()), response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({'error': f'Member service unavailable: {str(e)}'}), 503

    @app.route('/api/members/<int:user_id>', methods=['PUT'])
    def update_member(user_id):
        try:
            headers = {'Authorization': request.headers.get('Authorization')}
            response = requests.put(f"{MEMBER_SERVICE_URL}/members/{user_id}", 
                                 json=request.get_json(), 
                                 headers=headers)
            return jsonify(response.json()), response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({'error': f'Member service unavailable: {str(e)}'}), 503

    # Handle preflight OPTIONS requests for CORS
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = jsonify()
            # Allow requests from both localhost and frontend service
            origin = request.headers.get('Origin')
            if origin in ['http://localhost:4200', 'http://localhost:3000', 'http://frontend', 'http://localhost']:
                response.headers.add("Access-Control-Allow-Origin", origin)
            response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,X-Requested-With")
            response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
            response.headers.add('Access-Control-Allow-Credentials', "true")
            return response

    # Add CORS headers to all responses
    @app.after_request
    def after_request(response):
        # Allow requests from both localhost and frontend service
        origin = request.headers.get('Origin')
        if origin in ['http://localhost:4200', 'http://localhost:3000', 'http://frontend', 'http://localhost']:
            response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    return app

# For direct execution
if __name__ == '__main__':
    app = create_app()
    
    # Initialize database if it doesn't exist
    with app.app_context():
        if not os.path.exists(os.environ.get('DATABASE_URL', 'library.db')):
            init_db()
            seed_data()
            print("✅ Database initialized with seed data!")
            print("📚 Your book 'Do bailo ki gatha by prem chand' is included!")
    
    print("\n🚀 Starting Gateway server on port 5000")
    print("\n📋 API endpoints available:")
    print("- POST /api/login        - User login")
    print("- POST /api/signup       - User registration")
    print("- GET /api/books         - Get all books")
    print("- POST /api/books        - Create book (admin)")
    print("- PUT /api/books/<id>    - Update book (admin)")
    print("- DELETE /api/books/<id> - Delete book (admin)")
    print("- GET /api/transactions  - Get transactions")
    print("- POST /api/borrow/<book_id>       - Borrow a book")
    print("- POST /api/return/<transaction_id> - Return a book")
    print("- GET /api/members       - Get members (admin)")
    print("- PUT /api/members/<user_id> - Update member (admin)")
    print("\n🔑 Default credentials:")
    print("- Admin: admin@library.com / admin123")
    print("- Member: member@library.com / member123")
    print("- Member: jane@library.com / jane123")
    print("\n🎯 Gateway is ready for Docker Compose deployment!")
    
    app.run(debug=True, port=5000, host='0.0.0.0')
