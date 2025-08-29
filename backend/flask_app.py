from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, verify_jwt_in_request, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Configuration
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
jwt = JWTManager(app)
CORS(app, origins=['http://localhost:4200', 'http://localhost:3000', 'http://frontend', 'http://localhost'])

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

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
        seed_data()
        print("Database initialized with seed data!")
    
    print("Starting Flask server on port 5000")
    print("Your book 'Do bailo ki gatha' is included in the database!")
    
    app.run(debug=True, port=5000, host='0.0.0.0')


