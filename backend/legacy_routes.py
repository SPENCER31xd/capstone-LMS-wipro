"""
Legacy routes for backward compatibility
These routes maintain the same API structure as the original app.py
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime, timedelta
import os

legacy_bp = Blueprint('legacy', __name__)

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

# Legacy Authentication Routes
@legacy_bp.route('/login', methods=['POST'])
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
        'id': user_row['id'],
        'email': user_row['email'],
        'password': password,
        'firstName': user_row['firstName'],
        'lastName': user_row['lastName'],
        'role': user_row['role'],
        'createdAt': user_row['createdAt'],
        'isActive': bool(user_row['isActive'])
    }

    # Create JWT token
    from flask_jwt_extended import create_access_token
    token = create_access_token(identity=user_row['id'])

    return jsonify({
        'user': user,
        'token': token
    })

@legacy_bp.route('/signup', methods=['POST'])
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
        'id': user_id,
        'email': email,
        'password': password,
        'firstName': firstName,
        'lastName': lastName,
        'role': role,
        'createdAt': datetime.now().isoformat(),
        'isActive': True
    }

    # Create JWT token
    from flask_jwt_extended import create_access_token
    token = create_access_token(identity=user_id)

    return jsonify({
        'user': user,
        'token': token
    })

# Legacy Book Routes
@legacy_bp.route('/books', methods=['GET'])
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
        books.append(book)

    return jsonify(books)

@legacy_bp.route('/books/<int:book_id>', methods=['GET'])
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

# Legacy Transaction Routes
@legacy_bp.route('/borrow/<int:book_id>', methods=['POST'])
def borrow_book(book_id):
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()

        data = request.get_json() or {}
        due_date = data.get('dueDate')

        if not due_date:
            due_date = datetime.now() + timedelta(days=14)
        else:
            try:
                if isinstance(due_date, str):
                    if 'T' in due_date:
                        due_date = datetime.fromisoformat(due_date.replace('Z', ''))
                    else:
                        due_date = datetime.strptime(due_date, '%Y-%m-%d')
            except:
                due_date = datetime.now() + timedelta(days=14)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        book_row = cursor.fetchone()

        if not book_row:
            conn.close()
            return jsonify({'error': 'Book not found'}), 404

        if book_row[8] <= 0:
            conn.close()
            return jsonify({'error': 'Book not available'}), 400

        cursor.execute("SELECT id FROM transactions WHERE bookId = ? AND userId = ? AND status = 'active'", (book_id, current_user_id))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'User already has this book'}), 400

        issue_date = datetime.now()
        cursor.execute('''
            INSERT INTO transactions (bookId, userId, type, issueDate, dueDate, status)
            VALUES (?, ?, 'issue', ?, ?, 'active')
        ''', (book_id, current_user_id, issue_date, due_date))

        transaction_id = cursor.lastrowid
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
        return jsonify({'error': 'Authentication required'}), 401

@legacy_bp.route('/return/<int:transaction_id>', methods=['POST'])
def return_book(transaction_id):
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()

        data = request.get_json() or {}
        return_date = data.get('returnDate')

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

        cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
        transaction_row = cursor.fetchone()

        if not transaction_row:
            conn.close()
            return jsonify({'error': 'Transaction not found'}), 404

        if transaction_row['status'] != 'active':
            conn.close()
            return jsonify({'error': 'Book is not currently issued'}), 400

        cursor.execute("SELECT role FROM users WHERE id = ?", (current_user_id,))
        user_role = cursor.fetchone()['role']

        if user_role != 'admin' and transaction_row['userId'] != current_user_id:
            conn.close()
            return jsonify({'error': 'You can only return your own books'}), 403

        due_date = datetime.fromisoformat(transaction_row['dueDate'])
        if return_date > due_date:
            days_overdue = (return_date - due_date).days
            fine = days_overdue * 10
        else:
            fine = 0

        cursor.execute('''
            UPDATE transactions
            SET returnDate = ?, status = 'returned', fine = ?, updatedAt = ?
            WHERE id = ?
        ''', (return_date, fine, datetime.now(), transaction_id))

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

# Initialize database when module is imported
if not os.path.exists(DATABASE):
    init_db()
    seed_data()
