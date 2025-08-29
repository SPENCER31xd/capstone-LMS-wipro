from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, verify_jwt_in_request, get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)

# Configuration
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
jwt = JWTManager(app)

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

# Configure CORS properly for Angular frontend
CORS(app, 
     origins=['http://localhost:4200', 'http://localhost:3000', 'http://frontend', 'http://localhost'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
     supports_credentials=True)

# Database setup
DATABASE = 'library.db'

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
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', transactions)

    conn.commit()
    conn.close()

# JWT Authentication Decorators
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

def jwt_required_custom(fn):
    """Custom JWT decorator with better error handling"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authentication required'}), 401
    
    return wrapper

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

# Book API Routes - Match Angular expectations
@app.route('/api/books', methods=['GET'])
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

@app.route('/api/books/<int:book_id>', methods=['GET'])
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

@app.route('/api/books', methods=['POST'])
def create_book():
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()

        # Check if user is admin
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE id = ?", (current_user_id,))
        user_role = cursor.fetchone()

        if not user_role or user_role[0] != 'admin':
            conn.close()
            return jsonify({'error': 'Admin access required'}), 403

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
            conn.close()
            return jsonify({'error': 'Required fields missing'}), 400

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
    except Exception as e:
        return jsonify({'error': 'Authentication required'}), 401

@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()

        # Check if user is admin
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE id = ?", (current_user_id,))
        user_role = cursor.fetchone()

        if not user_role or user_role[0] != 'admin':
            conn.close()
            return jsonify({'error': 'Admin access required'}), 403

        data = request.get_json()

        # Get current book
        conn.row_factory = sqlite3.Row
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
    except Exception as e:
        return jsonify({'error': 'Authentication required'}), 401

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()

        # Check if user is admin
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE id = ?", (current_user_id,))
        user_role = cursor.fetchone()

        if not user_role or user_role[0] != 'admin':
            conn.close()
            return jsonify({'error': 'Admin access required'}), 403

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
    except Exception as e:
        return jsonify({'error': 'Authentication required'}), 401

@app.route('/api/borrow/<int:book_id>', methods=['POST'])
def borrow_book(book_id):
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()

        data = request.get_json() or {}
        due_date = data.get('dueDate')

        # Default due date to 14 days from now if not provided
        if not due_date:
            due_date = datetime.now() + timedelta(days=14)
        else:
            try:
                # Handle different date formats
                if isinstance(due_date, str):
                    if 'T' in due_date:
                        due_date = datetime.fromisoformat(due_date.replace('Z', ''))
                    else:
                        due_date = datetime.strptime(due_date, '%Y-%m-%d')
            except:
                due_date = datetime.now() + timedelta(days=14)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Check if book exists and is available
        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        book_row = cursor.fetchone()

        if not book_row:
            conn.close()
            return jsonify({'error': 'Book not found'}), 404

        # Check available copies (index 8 is availableCopies)
        if book_row[8] <= 0:
            conn.close()
            return jsonify({'error': 'Book not available'}), 400

        # Check if user already has this book
        cursor.execute("SELECT id FROM transactions WHERE bookId = ? AND userId = ? AND status = 'active'", (book_id, current_user_id))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'User already has this book'}), 400

        # Create transaction
        issue_date = datetime.now()
        cursor.execute('''
            INSERT INTO transactions (bookId, userId, type, issueDate, dueDate, status)
            VALUES (?, ?, 'issue', ?, ?, 'active')
        ''', (book_id, current_user_id, issue_date, due_date))

        transaction_id = cursor.lastrowid

        # Update book availability
        cursor.execute("UPDATE books SET availableCopies = availableCopies - 1, updatedAt = ? WHERE id = ?", (datetime.now(), book_id))

        conn.commit()
        conn.close()

        transaction = {
            'id': str(transaction_id),
            'bookId': int(book_id),
            'userId': str(current_user_id),
            'type': 'issue',
            'issueDate': issue_date.isoformat(),
            'dueDate': due_date.isoformat(),
            'returnDate': None,
            'status': 'active',
            'fine': 0,
            'createdAt': issue_date.isoformat(),
            'updatedAt': issue_date.isoformat()
        }

        return jsonify(transaction), 201
    except Exception as e:
        # Return proper JSON error response
        error_message = str(e) if str(e) else 'Authentication required'
        response = jsonify({'error': error_message, 'success': False})
        return response, 401

@app.route('/api/return/<int:transaction_id>', methods=['POST'])
def return_book(transaction_id):
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()

        data = request.get_json() or {}
        return_date = data.get('returnDate')

        # Default return date to now if not provided
        if not return_date:
            return_date = datetime.now()
        else:
            try:
                if isinstance(return_date, str):
                    if 'T' in return_date:
                        return_date = datetime.fromisoformat(return_date.replace('Z', ''))
                    else:
                        return_date = datetime.strptime(return_date, '%Y-%m-%d')
            except:
                return_date = datetime.now()

        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get transaction
        cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
        transaction_row = cursor.fetchone()

        if not transaction_row:
            conn.close()
            return jsonify({'error': 'Transaction not found'}), 404

        if transaction_row['status'] != 'active':
            conn.close()
            return jsonify({'error': 'Book is not currently issued'}), 400

        # Check if user owns this transaction (unless admin)
        cursor.execute("SELECT role FROM users WHERE id = ?", (current_user_id,))
        user_role = cursor.fetchone()['role']

        if user_role != 'admin' and transaction_row['userId'] != current_user_id:
            conn.close()
            return jsonify({'error': 'You can only return your own books'}), 403

        # Calculate fine if overdue
        due_date = datetime.fromisoformat(transaction_row['dueDate'])
        if return_date > due_date:
            days_overdue = (return_date - due_date).days
            fine = days_overdue * 10  # $10 per day
        else:
            fine = 0

        # Update transaction
        cursor.execute('''
            UPDATE transactions
            SET returnDate = ?, status = 'returned', fine = ?, updatedAt = ?
            WHERE id = ?
        ''', (return_date, fine, datetime.now(), transaction_id))

        # Update book availability
        cursor.execute("UPDATE books SET availableCopies = availableCopies + 1, updatedAt = ? WHERE id = ?",
                       (datetime.now(), transaction_row['bookId']))

        conn.commit()
        conn.close()

        transaction = {
            'id': str(transaction_id),
            'bookId': str(transaction_row['bookId']),
            'userId': str(transaction_row['userId']),
            'type': 'return',
            'issueDate': transaction_row['issueDate'],
            'dueDate': transaction_row['dueDate'],
            'returnDate': return_date.isoformat(),
            'status': 'returned',
            'fine': fine,
            'createdAt': transaction_row['createdAt'],
            'updatedAt': datetime.now().isoformat()
        }

        return jsonify(transaction)
    except Exception as e:
        return jsonify({'error': 'Authentication required'}), 401

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()

        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get current user to check if admin
        cursor.execute("SELECT role FROM users WHERE id = ?", (current_user_id,))
        user_role = cursor.fetchone()['role']

        # Build query based on user role
        if user_role == 'admin':
            cursor.execute('''
                SELECT t.*, u.firstName, u.lastName, u.email, b.title, b.author, b.isbn
                FROM transactions t
                JOIN users u ON t.userId = u.id
                JOIN books b ON t.bookId = b.id
                ORDER BY t.createdAt DESC
            ''')
        else:
            cursor.execute('''
                SELECT t.*, u.firstName, u.lastName, u.email, b.title, b.author, b.isbn
                FROM transactions t
                JOIN users u ON t.userId = u.id
                JOIN books b ON t.bookId = b.id
                WHERE t.userId = ?
                ORDER BY t.createdAt DESC
            ''', (current_user_id,))

        transactions_rows = cursor.fetchall()
        conn.close()

        transactions = []
        for t_row in transactions_rows:
            transaction = {
                'id': str(t_row['id']),
                'bookId': str(t_row['bookId']),
                'userId': str(t_row['userId']),
                'type': t_row['type'],
                'issueDate': t_row['issueDate'],
                'dueDate': t_row['dueDate'],
                'returnDate': t_row['returnDate'],
                'status': t_row['status'],
                'fine': t_row['fine'] or 0,
                'createdAt': t_row['createdAt'],
                'updatedAt': t_row['updatedAt'],
                'book': {
                    'title': t_row['title'],
                    'author': t_row['author'],
                    'isbn': t_row['isbn'] or ''
                },
                'user': {
                    'firstName': t_row['firstName'],
                    'lastName': t_row['lastName'],
                    'email': t_row['email']
                }
            }
            transactions.append(transaction)

        return jsonify(transactions)
    except Exception as e:
        return jsonify({'error': 'Authentication required'}), 401

@app.route('/api/members', methods=['GET'])
@admin_required
def get_members():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE role = 'member' ORDER BY createdAt DESC")
        members_rows = cursor.fetchall()
        conn.close()

        members = []
        for member_row in members_rows:
            member = {
                'id': member_row['id'],  # Keep as integer for Angular
                'email': member_row['email'],
                'password': '',  # Don't return password
                'firstName': member_row['firstName'],
                'lastName': member_row['lastName'],
                'role': member_row['role'],
                'createdAt': member_row['createdAt'],
                'isActive': bool(member_row['isActive'])
            }
            members.append(member)

        return jsonify(members)
    except Exception as e:
        return jsonify({'error': 'Failed to fetch members'}), 500

@app.route('/api/members/<int:user_id>', methods=['PUT'])
@admin_required
def update_member(user_id):
    try:
        data = request.get_json()
        is_active = data.get('isActive')

        if is_active is None:
            return jsonify({'error': 'isActive field is required'}), 400

        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ? AND role = 'member'", (user_id,))
        member_row = cursor.fetchone()

        if not member_row:
            conn.close()
            return jsonify({'error': 'Member not found'}), 404

        cursor.execute("UPDATE users SET isActive = ? WHERE id = ?", (is_active, user_id))
        conn.commit()
        conn.close()

        member = {
            'id': user_id,  # Keep as integer for Angular
            'email': member_row['email'],
            'password': '',
            'firstName': member_row['firstName'],
            'lastName': member_row['lastName'],
            'role': member_row['role'],
            'createdAt': member_row['createdAt'],
            'isActive': is_active
        }

        return jsonify(member)
    except Exception as e:
        return jsonify({'error': 'Failed to update member'}), 500

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

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
        seed_data()
        print("✅ Database initialized with seed data!")
        print("📚 Your book 'Do bailo ki gatha by prem chand' is included!")

    print("\n🚀 Starting Flask server on port 5000")
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
    print("\n🎯 Server is ready for Docker Compose deployment!")

    app.run(debug=True, port=5000, host='0.0.0.0')

