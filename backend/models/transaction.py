from extensions import db
from datetime import datetime, timedelta
from enum import Enum

class TransactionStatus(Enum):
    ISSUED = "issued"
    RETURNED = "returned"
    OVERDUE = "overdue"

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    issue_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum(TransactionStatus), nullable=False, default=TransactionStatus.ISSUED)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, user_id, book_id, days_to_return=14):
        self.user_id = user_id
        self.book_id = book_id
        self.issue_date = datetime.utcnow()
        self.due_date = self.issue_date + timedelta(days=days_to_return)
        self.status = TransactionStatus.ISSUED
    
    def is_overdue(self):
        """Check if transaction is overdue"""
        return datetime.utcnow() > self.due_date and self.status == TransactionStatus.ISSUED
    
    def return_book(self):
        """Mark book as returned"""
        self.return_date = datetime.utcnow()
        self.status = TransactionStatus.RETURNED
    
    def days_overdue(self):
        """Calculate days overdue"""
        if self.is_overdue():
            return (datetime.utcnow() - self.due_date).days
        return 0
    
    def to_dict(self):
        """Convert transaction to dictionary"""
        return {
            'id': self.id,
            'userId': self.user_id,
            'bookId': self.book_id,
            'issueDate': self.issue_date.isoformat(),
            'returnDate': self.return_date.isoformat() if self.return_date else None,
            'status': self.status.value
        }
    
    def __repr__(self):
        return f'<Transaction {self.id}: User {self.user_id} - Book {self.book_id}>'
