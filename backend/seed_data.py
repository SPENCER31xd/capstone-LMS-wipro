#!/usr/bin/env python3
"""
Seed data script for Library Management System
Run this script to populate the database with sample data
"""

from gateway import create_app
from extensions import db

def create_users():
    """Create sample users"""
    try:
        from models.user import User, UserRole, UserStatus
        
        users_data = [
            {
                'name': 'Admin User',
                'email': 'admin@library.com',
                'password': 'admin123',
                'role': UserRole.ADMIN
            },
            {
                'name': 'John Doe',
                'email': 'john@example.com',
                'password': 'password123',
                'role': UserRole.MEMBER
            },
            {
                'name': 'Jane Smith',
                'email': 'jane@example.com',
                'password': 'password123',
                'role': UserRole.MEMBER
            },
            {
                'name': 'Bob Johnson',
                'email': 'bob@example.com',
                'password': 'password123',
                'role': UserRole.MEMBER
            },
            {
                'name': 'Alice Brown',
                'email': 'alice@example.com',
                'password': 'password123',
                'role': UserRole.MEMBER
            }
        ]
        
        created_users = []
        for user_data in users_data:
            existing_user = User.query.filter_by(email=user_data['email']).first()
            if existing_user:
                print(f"User {user_data['email']} already exists, skipping...")
                created_users.append(existing_user)
                continue
            
            user = User(
                name=user_data['name'],
                email=user_data['email'],
                role=user_data['role'],
                status=UserStatus.ACTIVE
            )
            user.set_password(user_data['password'])
            
            db.session.add(user)
            created_users.append(user)
            print(f"Created user: {user_data['name']} ({user_data['email']})")
        
        db.session.commit()
        return created_users
        
    except ImportError:
        print("Note: Using legacy database structure")
        from legacy_routes import seed_data
        seed_data()
        return []

def create_books():
    """Create sample books"""
    try:
        from models.book import Book
        
        books_data = [
            {
                'title': 'To Kill a Mockingbird',
                'author': 'Harper Lee',
                'category': 'Fiction',
                'total_copies': 5
            },
            {
                'title': '1984',
                'author': 'George Orwell',
                'category': 'Fiction',
                'total_copies': 3
            },
            {
                'title': 'Pride and Prejudice',
                'author': 'Jane Austen',
                'category': 'Fiction',
                'total_copies': 4
            },
            {
                'title': 'The Great Gatsby',
                'author': 'F. Scott Fitzgerald',
                'category': 'Fiction',
                'total_copies': 6
            },
            {
                'title': 'Clean Code',
                'author': 'Robert C. Martin',
                'category': 'Technology',
                'total_copies': 4
            },
            {
                'title': 'Do bailo ki gatha',
                'author': 'prem chand',
                'category': 'Fiction',
                'total_copies': 2
            }
        ]
        
        created_books = []
        for book_data in books_data:
            existing_book = Book.query.filter_by(
                title=book_data['title'], 
                author=book_data['author']
            ).first()
            
            if existing_book:
                print(f"Book '{book_data['title']}' already exists, skipping...")
                created_books.append(existing_book)
                continue
            
            book = Book(
                title=book_data['title'],
                author=book_data['author'],
                category=book_data['category'],
                total_copies=book_data['total_copies'],
                available_copies=book_data['total_copies']
            )
            
            db.session.add(book)
            created_books.append(book)
            print(f"Created book: {book_data['title']} by {book_data['author']}")
        
        db.session.commit()
        return created_books
        
    except ImportError:
        print("Note: Using legacy database structure")
        return []

def main():
    """Main function to seed the database"""
    print("=" * 60)
    print("Library Management System - Database Seeding")
    print("=" * 60)
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        print("Creating users...")
        users = create_users()
        
        print("Creating books...")
        books = create_books()
        
        print("\n" + "=" * 60)
        print("Database seeding completed!")
        print(f"Created {len(users)} users and {len(books)} books")
        print("=" * 60)

if __name__ == '__main__':
    main()
