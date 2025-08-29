# Transaction endpoints
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
import sqlite3
from datetime import datetime, timedelta

def add_transaction_routes(app):
    """Add transaction routes to the Flask app"""
    
    @app.route('/api/transactions', methods=['GET'])
    def get_transactions():
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        
        conn = sqlite3.connect('library.db')
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

    @app.route('/api/borrow/<int:book_id>', methods=['POST'])
    def borrow_book(book_id):
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        
        data = request.get_json() or {}
        due_date = data.get('dueDate')
        
        # Default due date to 14 days from now if not provided
        if not due_date:
            due_date = datetime.now() + timedelta(days=14)
        else:
            due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # Check if book exists and is available
        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        book_row = cursor.fetchone()
        
        if not book_row:
            conn.close()
            return jsonify({'error': 'Book not found'}), 404
        
        if book_row[9] <= 0:  # availableCopies
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

    @app.route('/api/return/<int:transaction_id>', methods=['POST'])
    def return_book(transaction_id):
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        
        data = request.get_json() or {}
        return_date = data.get('returnDate')
        
        # Default return date to now if not provided
        if not return_date:
            return_date = datetime.now()
        else:
            return_date = datetime.fromisoformat(return_date.replace('Z', '+00:00'))
        
        conn = sqlite3.connect('library.db')
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
        fine = 0
        if return_date > due_date:
            overdue_days = (return_date - due_date).days
            fine = overdue_days * 1.0  # $1 per day
        
        # Update transaction
        cursor.execute('''
            UPDATE transactions 
            SET returnDate = ?, status = 'returned', fine = ?, updatedAt = ?
            WHERE id = ?
        ''', (return_date, fine, datetime.now(), transaction_id))
        
        # Update book availability
        cursor.execute("UPDATE books SET availableCopies = availableCopies + 1, updatedAt = ? WHERE id = ?", (datetime.now(), transaction_row['bookId']))
        
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


