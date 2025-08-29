# Book endpoints  
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request
import sqlite3
from datetime import datetime

def add_book_routes(app):
    """Add book routes to the Flask app"""
    
    @app.route('/api/books', methods=['GET'])
    def get_books():
        verify_jwt_in_request()
        
        conn = sqlite3.connect('library.db')
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

    @app.route('/api/books/<int:book_id>', methods=['GET'])
    def get_book(book_id):
        verify_jwt_in_request()
        
        conn = sqlite3.connect('library.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        book_row = cursor.fetchone()
        conn.close()
        
        if not book_row:
            return jsonify(None), 404
        
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
        verify_jwt_in_request()
        
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
        
        conn = sqlite3.connect('library.db')
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
            'isbn': isbn,
            'category': category,
            'publishedYear': publishedYear,
            'description': description,
            'totalCopies': totalCopies,
            'availableCopies': totalCopies,
            'imageUrl': imageUrl,
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat()
        }
        
        return jsonify(book), 201

    @app.route('/api/books/<int:book_id>', methods=['PUT'])
    def update_book(book_id):
        verify_jwt_in_request()
        
        data = request.get_json()
        
        conn = sqlite3.connect('library.db')
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

    @app.route('/api/books/<int:book_id>', methods=['DELETE'])
    def delete_book(book_id):
        verify_jwt_in_request()
        
        conn = sqlite3.connect('library.db')
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


