from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from extensions import db
from models.book import Book
from schemas.book_schema import BookCreateSchema, BookUpdateSchema, BookResponseSchema, BookSearchSchema
from utils.decorators import admin_required, active_user_required
from utils.helpers import success_response, error_response

books_bp = Blueprint('books', __name__)

# Initialize schemas
book_create_schema = BookCreateSchema()
book_update_schema = BookUpdateSchema()
book_response_schema = BookResponseSchema()
book_search_schema = BookSearchSchema()

@books_bp.route('', methods=['GET'])
@active_user_required
def get_books():
    """Get all books with optional filtering"""
    try:
        # Parse query parameters
        search_params = book_search_schema.load(request.args)
    except ValidationError as err:
        return error_response("Invalid search parameters", 400, err.messages)
    
    # Build query
    query = Book.query
    
    if search_params.get('title'):
        query = query.filter(Book.title.ilike(f"%{search_params['title']}%"))
    
    if search_params.get('author'):
        query = query.filter(Book.author.ilike(f"%{search_params['author']}%"))
    
    if search_params.get('category'):
        query = query.filter(Book.category.ilike(f"%{search_params['category']}%"))
    
    if search_params.get('available_only'):
        query = query.filter(Book.available_copies > 0)
    
    books = query.all()
    
    return [book.to_dict() for book in books]

@books_bp.route('/<int:book_id>', methods=['GET'])
@active_user_required
def get_book(book_id):
    """Get a specific book"""
    book = Book.query.get(book_id)
    
    if not book:
        return error_response("Book not found", 404)
    
    return book.to_dict()

@books_bp.route('', methods=['POST'])
@admin_required
def create_book():
    """Create a new book (admin only)"""
    try:
        data = book_create_schema.load(request.json)
    except ValidationError as err:
        return error_response("Validation failed", 400, err.messages)
    
    # Check if book already exists
    existing_book = Book.query.filter_by(
        title=data['title'], 
        author=data['author']
    ).first()
    
    if existing_book:
        return error_response("Book with same title and author already exists", 400)
    
    # Create new book
    book = Book(
        title=data['title'],
        author=data['author'],
        category=data['category'],
        total_copies=data['total_copies'],
        available_copies=data['total_copies']
    )
    
    try:
        db.session.add(book)
        db.session.commit()
        
        return book.to_dict(), 201
        
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to create book", 500)

@books_bp.route('/<int:book_id>', methods=['PUT'])
@admin_required
def update_book(book_id):
    """Update a book (admin only)"""
    book = Book.query.get(book_id)
    
    if not book:
        return error_response("Book not found", 404)
    
    try:
        data = book_update_schema.load(request.json)
    except ValidationError as err:
        return error_response("Validation failed", 400, err.messages)
    
    # Update book fields
    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'category' in data:
        book.category = data['category']
    if 'total_copies' in data:
        # Ensure available copies don't exceed total copies
        new_total = data['total_copies']
        current_issued = book.total_copies - book.available_copies
        
        if new_total < current_issued:
            return error_response(
                f"Cannot reduce total copies below {current_issued} (currently issued)",
                400
            )
        
        book.available_copies = new_total - current_issued
        book.total_copies = new_total
    
    try:
        db.session.commit()
        
        return book.to_dict()
        
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to update book", 500)

@books_bp.route('/<int:book_id>', methods=['DELETE'])
@admin_required
def delete_book(book_id):
    """Delete a book (admin only)"""
    book = Book.query.get(book_id)
    
    if not book:
        return error_response("Book not found", 404)
    
    # Check if book is currently issued
    current_issued = book.total_copies - book.available_copies
    if current_issued > 0:
        return error_response(
            f"Cannot delete book. {current_issued} copies are currently issued",
            400
        )
    
    try:
        db.session.delete(book)
        db.session.commit()
        
        return {'success': True, 'message': 'Book deleted successfully'}
        
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to delete book", 500)

@books_bp.route('/categories', methods=['GET'])
@active_user_required
def get_categories():
    """Get all unique book categories"""
    categories = db.session.query(Book.category).distinct().all()
    category_list = [cat[0] for cat in categories if cat[0]]
    
    return category_list
