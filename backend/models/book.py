from extensions import db
from datetime import datetime

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    total_copies = db.Column(db.Integer, nullable=False, default=1)
    available_copies = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='book', lazy=True)
    
    def is_available(self):
        """Check if book is available for borrowing"""
        return self.available_copies > 0
    
    def borrow_book(self):
        """Decrease available copies when borrowed"""
        if self.available_copies > 0:
            self.available_copies -= 1
            return True
        return False
    
    def return_book(self):
        """Increase available copies when returned"""
        if self.available_copies < self.total_copies:
            self.available_copies += 1
            return True
        return False
    
    def to_dict(self):
        """Convert book to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'category': self.category,
            'availableCopies': self.available_copies,
            'totalCopies': self.total_copies
        }
    
    def __repr__(self):
        return f'<Book {self.title} by {self.author}>'
