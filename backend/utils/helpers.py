from flask import jsonify
from marshmallow import ValidationError

def handle_validation_error(error):
    """Handle marshmallow validation errors"""
    return jsonify({
        'error': 'Validation failed',
        'messages': error.messages
    }), 400

def success_response(data=None, message="Success", status_code=200):
    """Standard success response format"""
    response = {'status': 'success', 'message': message}
    if data is not None:
        response['data'] = data
    return jsonify(response), status_code

def error_response(message="Error occurred", status_code=400, errors=None):
    """Standard error response format for frontend compatibility"""
    response = {'success': False, 'message': message}
    if errors:
        response['errors'] = errors
    return jsonify(response), status_code

def legacy_error_response(message="Error occurred", status_code=400, errors=None):
    """Legacy error response format"""
    response = {'status': 'error', 'message': message}
    if errors:
        response['errors'] = errors
    return jsonify(response), status_code
