from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, verify_jwt_in_request, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import logging
from datetime import datetime, timedelta

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('library_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
jwt = JWTManager(app)

# Add JWT error handlers for better debugging
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    logger.error(f"JWT token expired: {jwt_payload}")
    return jsonify({'error': 'Token has expired'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    logger.error(f"Invalid JWT token: {error}")
    return jsonify({'error': f'Invalid token: {error}'}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    logger.error(f"Missing JWT token: {error}")
    return jsonify({'error': f'Missing token: {error}'}), 401



# Configure CORS for Angular frontend
CORS(app, 
     origins=['http://localhost:4200', 'http://localhost:3000', 'http://frontend', 'http://localhost'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
     supports_credentials=True,
     send_wildcard=False)

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
        INSERT INTO transactions (bookId, userId, type, issueDate, dueDate, status, fine)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', transactions)

    conn.commit()
    conn.close()

# Authentication Routes - Match Angular expectations
@app.route('/api/login', methods=['POST'])
def auth_login():
    logger.info(f"Login attempt from IP: {request.remote_addr}")
    
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    logger.info(f"Login attempt for email: {email}")

    if not email or not password:
        logger.warning(f"Login attempt with missing credentials - Email: {bool(email)}, Password: {bool(password)}")
        return jsonify({'error': 'Email and password are required'}), 400

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user_row = cursor.fetchone()
    conn.close()

    if not user_row or not check_password_hash(user_row['password'], password):
        logger.warning(f"Failed login attempt for email: {email}")
        return jsonify({'error': 'Invalid email or password'}), 401

    if not user_row['isActive']:
        logger.warning(f"Login attempt for inactive account: {email}")
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

        # Create JWT token - convert ID to string for JWT compatibility
    token = create_access_token(identity=str(user_row['id']))
    
    logger.info(f"Successful login for user: {email} (ID: {user_row['id']}, Role: {user_row['role']})")

    return jsonify({
        'user': user,
        'token': token
    })

@app.route('/api/signup', methods=['POST'])
def auth_signup():
    logger.info(f"Signup attempt from IP: {request.remote_addr}")
    
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    firstName = data.get('firstName')
    lastName = data.get('lastName')
    role = data.get('role', 'member')
    
    logger.info(f"Signup attempt for email: {email}, role: {role}")

    if not all([email, password, firstName, lastName]):
        logger.warning(f"Signup attempt with missing fields - Email: {bool(email)}, Password: {bool(password)}, FirstName: {bool(firstName)}, LastName: {bool(lastName)}")
        return jsonify({'error': 'All fields are required'}), 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Check if user already exists
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        logger.warning(f"Signup attempt with existing email: {email}")
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
    
    logger.info(f"Successfully created new user: {email} (ID: {user_id}, Role: {role})")

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
    
    logger.info(f"JWT token generated for new user: {email}")

    return jsonify({
        'user': user,
        'token': token
    })

# Book API Routes - Match Angular expectations
@app.route('/api/books', methods=['GET'])
def get_books():
    logger.info(f"Get books request from IP: {request.remote_addr}")
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM books ORDER BY createdAt DESC")
    books_rows = cursor.fetchall()
    conn.close()
    
    logger.info(f"Retrieved {len(books_rows)} books from database")

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

    logger.info(f"Successfully returned {len(books)} books to client")
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
        # Verify JWT token with detailed error logging
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            # Convert string ID to integer for database queries
            current_user_id = int(current_user_id) if current_user_id else None
            logger.info(f"JWT verification successful for user ID: {current_user_id}")
        except Exception as jwt_error:
            logger.error(f"JWT verification failed: {str(jwt_error)}")
            logger.error(f"Request headers: {dict(request.headers)}")
            return jsonify({'error': f'JWT verification failed: {str(jwt_error)}'}), 401

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
        # Verify JWT token with detailed error logging
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            # Convert string ID to integer for database queries
            current_user_id = int(current_user_id) if current_user_id else None
            logger.info(f"JWT verification successful for user ID: {current_user_id}")
        except Exception as jwt_error:
            logger.error(f"JWT verification failed: {str(jwt_error)}")
            logger.error(f"Request headers: {dict(request.headers)}")
            return jsonify({'error': f'JWT verification failed: {str(jwt_error)}'}), 401

        # Check if user is admin
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE id = ?", (current_user_id,))
        user_role = cursor.fetchone()

        if not user_role or user_role[0] != 'admin':
            conn.close()
            return jsonify({'error': 'Admin access required'}), 403

        data = request.get_json()

        # Set row_factory BEFORE creating new cursor
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()  # Create new cursor with row_factory
        
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
    except Exception as e:
        print(f"Error in update_book: {e}")
        return jsonify({'error': 'Authentication required'}), 401

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    try:
        # Verify JWT token with detailed error logging
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            # Convert string ID to integer for database queries
            current_user_id = int(current_user_id) if current_user_id else None
            logger.info(f"JWT verification successful for user ID: {current_user_id}")
        except Exception as jwt_error:
            logger.error(f"JWT verification failed: {str(jwt_error)}")
            logger.error(f"Request headers: {dict(request.headers)}")
            return jsonify({'error': f'JWT verification failed: {str(jwt_error)}'}), 401

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
        logger.info(f"Borrow book request for book ID: {book_id} from IP: {request.remote_addr}")
        
        # Verify JWT token with detailed error logging
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            # Convert string ID to integer for database queries
            current_user_id = int(current_user_id) if current_user_id else None
            logger.info(f"JWT verification successful for user ID: {current_user_id}")
        except Exception as jwt_error:
            logger.error(f"JWT verification failed: {str(jwt_error)}")
            logger.error(f"Request headers: {dict(request.headers)}")
            return jsonify({'error': f'JWT verification failed: {str(jwt_error)}'}), 401
        
        logger.info(f"User ID {current_user_id} attempting to borrow book ID {book_id}")

        data = request.get_json() or {}
        due_date = data.get('dueDate')

        # Default due date to 14 days from now if not provided
        if not due_date:
            due_date = datetime.now() + timedelta(days=14)
            logger.info(f"Using default due date: {due_date}")
        else:
            try:
                # Handle different date formats
                if isinstance(due_date, str):
                    if 'T' in due_date:
                        due_date = datetime.fromisoformat(due_date.replace('Z', ''))
                    else:
                        due_date = datetime.strptime(due_date, '%Y-%m-%d')
                logger.info(f"Using provided due date: {due_date}")
            except Exception as e:
                due_date = datetime.now() + timedelta(days=14)
                logger.warning(f"Invalid due date format, using default: {e}")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Check if book exists and is available
        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        book_row = cursor.fetchone()

        if not book_row:
            conn.close()
            logger.warning(f"Book not found: ID {book_id}")
            return jsonify({'error': 'Book not found'}), 404

        logger.info(f"Found book: {book_row[1]} by {book_row[2]} (Available: {book_row[8]}/{book_row[7]})")

        # Check available copies (index 8 is availableCopies)
        if int(book_row[8]) <= 0:
            conn.close()
            logger.warning(f"Book ID {book_id} not available - no copies left")
            return jsonify({'error': 'Book not available'}), 400

        # Check if user already has this book
        cursor.execute("SELECT id FROM transactions WHERE bookId = ? AND userId = ? AND status = 'active'", (book_id, current_user_id))
        if cursor.fetchone():
            conn.close()
            logger.warning(f"User {current_user_id} already has book {book_id}")
            return jsonify({'error': 'User already has this book'}), 400

        # Create transaction
        issue_date = datetime.now()
        cursor.execute('''
            INSERT INTO transactions (bookId, userId, type, issueDate, dueDate, status)
            VALUES (?, ?, 'issue', ?, ?, 'active')
        ''', (book_id, current_user_id, issue_date, due_date))

        transaction_id = cursor.lastrowid
        logger.info(f"Created transaction ID {transaction_id} for user {current_user_id} borrowing book {book_id}")

        # Update book availability
        cursor.execute("UPDATE books SET availableCopies = availableCopies - 1, updatedAt = ? WHERE id = ?", (datetime.now(), book_id))
        logger.info(f"Updated book {book_id} availability (reduced by 1)")

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

        logger.info(f"Successfully completed book borrowing - User: {current_user_id}, Book: {book_id}, Transaction: {transaction_id}")
        return jsonify(transaction), 201
    except Exception as e:
        # Return proper JSON error response
        error_message = str(e) if str(e) else 'Authentication required'
        logger.error(f"Error in borrow_book: {error_message} for user attempting to borrow book {book_id}")
        response = jsonify({'error': error_message, 'success': False})
        return response, 401

@app.route('/api/return/<int:transaction_id>', methods=['POST'])
def return_book(transaction_id):
    try:
        logger.info(f"Return book request for transaction ID: {transaction_id} from IP: {request.remote_addr}")
        
        # Verify JWT token with detailed error logging
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            logger.info(f"JWT verification successful for user ID: {current_user_id}")
        except Exception as jwt_error:
            logger.error(f"JWT verification failed: {str(jwt_error)}")
            logger.error(f"Request headers: {dict(request.headers)}")
            return jsonify({'error': f'JWT verification failed: {str(jwt_error)}'}), 401
        
        logger.info(f"User ID {current_user_id} attempting to return transaction ID {transaction_id}")

        data = request.get_json() or {}
        return_date = data.get('returnDate')

        # Default return date to now if not provided
        if not return_date:
            return_date = datetime.now()
            logger.info(f"Using current time as return date: {return_date}")
        else:
            try:
                if isinstance(return_date, str):
                    if 'T' in return_date:
                        return_date = datetime.fromisoformat(return_date.replace('Z', ''))
                    else:
                        return_date = datetime.strptime(return_date, '%Y-%m-%d')
                logger.info(f"Using provided return date: {return_date}")
            except Exception as e:
                return_date = datetime.now()
                logger.warning(f"Invalid return date format, using current time: {e}")

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
        user_role = cursor.fetchone()[0]  # Access tuple index, not dictionary key

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
        # Verify JWT token with detailed error logging
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            logger.info(f"JWT verification successful for user ID: {current_user_id}")
        except Exception as jwt_error:
            logger.error(f"JWT verification failed: {str(jwt_error)}")
            logger.error(f"Request headers: {dict(request.headers)}")
            return jsonify({'error': f'JWT verification failed: {str(jwt_error)}'}), 401

        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get current user to check if admin
        cursor.execute("SELECT role FROM users WHERE id = ?", (current_user_id,))
        user_role = cursor.fetchone()[0]  # Access tuple index, not dictionary key

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
def get_members():
    try:
        # Verify JWT token with detailed error logging
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            logger.info(f"JWT verification successful for user ID: {current_user_id}")
        except Exception as jwt_error:
            logger.error(f"JWT verification failed: {str(jwt_error)}")
            logger.error(f"Request headers: {dict(request.headers)}")
            return jsonify({'error': f'JWT verification failed: {str(jwt_error)}'}), 401

        # Check if user is admin
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE id = ?", (current_user_id,))
        user_role = cursor.fetchone()

        if not user_role or user_role[0] != 'admin':
            conn.close()
            return jsonify({'error': 'Admin access required'}), 403

        # Set row_factory BEFORE creating new cursor
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()  # Create new cursor with row_factory
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
        print(f"Error in get_members: {e}")
        return jsonify({'error': 'Authentication required'}), 401

@app.route('/api/members/<int:user_id>', methods=['PUT'])
def update_member(user_id):
    try:
        # Verify JWT token with detailed error logging
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            logger.info(f"JWT verification successful for user ID: {current_user_id}")
        except Exception as jwt_error:
            logger.error(f"JWT verification failed: {str(jwt_error)}")
            logger.error(f"Request headers: {dict(request.headers)}")
            return jsonify({'error': f'JWT verification failed: {str(jwt_error)}'}), 401

        # Check if user is admin
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE id = ?", (current_user_id,))
        user_role = cursor.fetchone()

        if not user_role or user_role[0] != 'admin':
            conn.close()
            return jsonify({'error': 'Admin access required'}), 403

        data = request.get_json()
        is_active = data.get('isActive')

        if is_active is None:
            conn.close()
            return jsonify({'error': 'isActive field is required'}), 400

        # Set row_factory BEFORE creating new cursor
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()  # Create new cursor with row_factory
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
        print(f"Error in update_member: {e}")
        return jsonify({'error': 'Authentication required'}), 401

# Request logging middleware - merged with header debugging
@app.before_request
def log_request_info():
    logger.info(f"Incoming request: {request.method} {request.url} from {request.remote_addr}")
    
    # Add detailed header logging for JWT debugging
    logger.info("=== REQUEST HEADERS DEBUG ===")
    logger.info(f"Method: {request.method}")
    logger.info(f"URL: {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Authorization Header: {request.headers.get('Authorization', 'NOT FOUND')}")
    logger.info("=== END HEADERS DEBUG ===")

# CORS is now handled entirely by Flask-CORS extension above

if __name__ == '__main__':
    logger.info("Starting Library Management System Backend")
    
    if not os.path.exists(DATABASE):
        logger.info("Database not found, initializing...")
        init_db()
        seed_data()
        logger.info("Database initialized with seed data!")
        logger.info("Book 'Do bailo ki gatha by prem chand' included in seed data")
        print("✅ Database initialized with seed data!")
        print("📚 Your book 'Do bailo ki gatha by prem chand' is included!")
    else:
        logger.info("Database found, skipping initialization")

    logger.info("All API endpoints configured and ready")
    logger.info("CORS configured for Angular frontend and Docker services")
    
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
    
    logger.info("Starting Flask development server on 0.0.0.0:5000")
    app.run(debug=True, port=5000, host='0.0.0.0')

