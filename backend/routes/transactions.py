from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError
from datetime import datetime
from extensions import db
from models.book import Book
from models.user import User
from models.transaction import Transaction, TransactionStatus
from schemas.transaction_schema import (
    TransactionCreateSchema, TransactionReturnSchema, 
    TransactionResponseSchema, TransactionSearchSchema
)
from utils.decorators import admin_required, active_user_required, get_current_user
from utils.helpers import success_response, error_response

transactions_bp = Blueprint('transactions', __name__)

# Initialize schemas
transaction_create_schema = TransactionCreateSchema()
transaction_return_schema = TransactionReturnSchema()
transaction_response_schema = TransactionResponseSchema()
transaction_search_schema = TransactionSearchSchema()

@transactions_bp.route('', methods=['GET'])
@active_user_required
def get_transactions():
    """Get transactions (all for admin, own for members)"""
    current_user = get_current_user()
    
    try:
        search_params = transaction_search_schema.load(request.args)
    except ValidationError as err:
        return error_response("Invalid search parameters", 400, err.messages)
    
    # Build query
    query = Transaction.query.join(User).join(Book)
    
    # Non-admin users can only see their own transactions
    if not current_user.is_admin():
        query = query.filter(Transaction.user_id == current_user.id)
    else:
        # Admin can filter by user
        if search_params.get('user_id'):
            query = query.filter(Transaction.user_id == search_params['user_id'])
    
    # Filter by book
    if search_params.get('book_id'):
        query = query.filter(Transaction.book_id == search_params['book_id'])
    
    # Filter by status
    if search_params.get('status'):
        query = query.filter(Transaction.status == search_params['status'])
    
    # Filter overdue only
    if search_params.get('overdue_only'):
        query = query.filter(
            Transaction.due_date < datetime.utcnow(),
            Transaction.status == TransactionStatus.ISSUED
        )
    
    transactions = query.order_by(Transaction.created_at.desc()).all()
    
    # Return transaction data directly
    return [transaction.to_dict() for transaction in transactions]

@transactions_bp.route('/borrow', methods=['POST'])
@active_user_required
def borrow_book():
    """Borrow a book"""
    current_user = get_current_user()
    
    try:
        data = transaction_create_schema.load(request.json)
    except ValidationError as err:
        return error_response("Validation failed", 400, err.messages)
    
    # Get the book
    book = Book.query.get(data['book_id'])
    if not book:
        return error_response("Book not found", 404)
    
    # Check if book is available
    if not book.is_available():
        return error_response("Book is not available", 400)
    
    # Check if user already has this book
    existing_transaction = Transaction.query.filter_by(
        user_id=current_user.id,
        book_id=book.id,
        status=TransactionStatus.ISSUED
    ).first()
    
    if existing_transaction:
        return error_response("You have already borrowed this book", 400)
    
    # Check borrowing limit (e.g., max 5 books per user)
    active_transactions = Transaction.query.filter_by(
        user_id=current_user.id,
        status=TransactionStatus.ISSUED
    ).count()
    
    if active_transactions >= 5:
        return error_response("You have reached the maximum borrowing limit (5 books)", 400)
    
    # Create transaction
    transaction = Transaction(
        user_id=current_user.id,
        book_id=book.id,
        days_to_return=data.get('days_to_return', 14)
    )
    
    # Update book availability
    book.borrow_book()
    
    try:
        db.session.add(transaction)
        db.session.commit()
        
        return transaction.to_dict(), 201
        
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to borrow book", 500)

@transactions_bp.route('/return', methods=['POST'])
@active_user_required
def return_book():
    """Return a book"""
    current_user = get_current_user()
    
    try:
        data = transaction_return_schema.load(request.json)
    except ValidationError as err:
        return error_response("Validation failed", 400, err.messages)
    
    # Get the transaction
    transaction = Transaction.query.get(data['transaction_id'])
    if not transaction:
        return error_response("Transaction not found", 404)
    
    # Check if user owns this transaction (unless admin)
    if not current_user.is_admin() and transaction.user_id != current_user.id:
        return error_response("You can only return your own books", 403)
    
    # Check if book is already returned
    if transaction.status == TransactionStatus.RETURNED:
        return error_response("Book is already returned", 400)
    
    # Update transaction
    transaction.return_book()
    
    # Update book availability
    book = Book.query.get(transaction.book_id)
    book.return_book()
    
    try:
        db.session.commit()
        
        return transaction.to_dict()
        
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to return book", 500)

@transactions_bp.route('/my-books', methods=['GET'])
@active_user_required
def get_my_books():
    """Get current user's active transactions"""
    current_user = get_current_user()
    
    active_transactions = Transaction.query.filter_by(
        user_id=current_user.id,
        status=TransactionStatus.ISSUED
    ).join(Book).order_by(Transaction.created_at.desc()).all()
    
    return [transaction.to_dict() for transaction in active_transactions]

@transactions_bp.route('/history', methods=['GET'])
@active_user_required
def get_transaction_history():
    """Get user's transaction history"""
    current_user = get_current_user()
    
    transactions = Transaction.query.filter_by(
        user_id=current_user.id
    ).join(Book).order_by(Transaction.created_at.desc()).all()
    
    return [transaction.to_dict() for transaction in transactions]

@transactions_bp.route('/overdue', methods=['GET'])
@admin_required
def get_overdue_transactions():
    """Get all overdue transactions (admin only)"""
    overdue_transactions = Transaction.query.filter(
        Transaction.due_date < datetime.utcnow(),
        Transaction.status == TransactionStatus.ISSUED
    ).join(User).join(Book).order_by(Transaction.due_date).all()
    
    return [transaction.to_dict() for transaction in overdue_transactions]

@transactions_bp.route('/stats', methods=['GET'])
@admin_required
def get_transaction_stats():
    """Get transaction statistics (admin only)"""
    total_transactions = Transaction.query.count()
    active_transactions = Transaction.query.filter_by(status=TransactionStatus.ISSUED).count()
    returned_transactions = Transaction.query.filter_by(status=TransactionStatus.RETURNED).count()
    
    overdue_transactions = Transaction.query.filter(
        Transaction.due_date < datetime.utcnow(),
        Transaction.status == TransactionStatus.ISSUED
    ).count()
    
    stats = {
        'total_transactions': total_transactions,
        'active_transactions': active_transactions,
        'returned_transactions': returned_transactions,
        'overdue_transactions': overdue_transactions
    }
    
    return stats
