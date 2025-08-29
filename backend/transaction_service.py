from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity, jwt_required
import sqlite3
import os
from datetime import datetime, timedelta
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
    return jsonify({'status': 'healthy', 'service': 'transaction-service'})

# Transaction API Routes
@app.route('/borrow/<int:book_id>', methods=['POST'])
@jwt_required()
def borrow_book(book_id):
    try:
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

@app.route('/return/<int:transaction_id>', methods=['POST'])
@jwt_required()
def return_book(transaction_id):
    try:
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

@app.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    try:
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
    port = int(os.environ.get('PORT', 5003))
    app.run(debug=True, port=port, host='0.0.0.0')

