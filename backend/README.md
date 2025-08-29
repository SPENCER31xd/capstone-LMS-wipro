# Library Management System - Backend

A modern, modular Flask backend for the Library Management System with API Gateway pattern.

## 🏗 Architecture

### 🚪 API Gateway Pattern
- **`gateway.py`** - Main application factory and entry point
- **Modular Blueprints** for organized route management
- **Legacy compatibility** maintained for existing functionality

### 📁 Project Structure
```
backend/
├── gateway.py              # 🚪 Main API Gateway & App Factory
├── legacy_routes.py        # 🔄 Backward compatibility routes
├── routes/                 # 📍 Modular route blueprints
│   ├── auth.py            # 🔑 Authentication routes
│   ├── books.py           # 📚 Book management routes
│   ├── transactions.py    # 🔄 Transaction routes
│   └── members.py         # 👥 Member management routes
├── models/                 # 🗄️ Database models
├── schemas/                # 📋 Data validation schemas
├── utils/                  # 🛠️ Utility functions & decorators
├── extensions.py           # 🔌 Flask extensions
└── config.py              # ⚙️ Configuration settings
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Gateway
```bash
# Option 1: Direct execution
python gateway.py

# Option 2: Using the automated setup
python run.py

# Option 3: Test the gateway structure
python test_gateway.py
```

The API will be available at `http://localhost:5000`

## 🔌 API Endpoints

### 🔑 Authentication (`/api/auth`)
- `POST /api/auth/login` - User login
- `POST /api/auth/signup` - User registration
- `GET /api/auth/profile` - Get user profile
- `GET /api/auth/verify` - Verify JWT token

### 📚 Books (`/api/books`)
- `GET /api/books` - Get all books with search/filter
- `GET /api/books/<id>` - Get specific book
- `POST /api/books` - Create book (Admin only)
- `PUT /api/books/<id>` - Update book (Admin only)
- `DELETE /api/books/<id>` - Delete book (Admin only)

### 🔄 Transactions (`/api/transactions`)
- `GET /api/transactions` - Get transactions
- `POST /api/transactions` - Create transaction (borrow/return)

### 👥 Members (`/api/members`)
- `GET /api/members` - Get all members (Admin only)
- `PUT /api/members/<id>` - Update member status (Admin only)

### 🔄 Legacy Routes (`/api/*`)
- `POST /api/login` - Legacy login (backward compatibility)
- `POST /api/signup` - Legacy signup (backward compatibility)
- `GET /api/books` - Legacy books endpoint
- `POST /api/borrow/<book_id>` - Legacy borrow endpoint
- `POST /api/return/<transaction_id>` - Legacy return endpoint

## 🔑 Default Login Credentials

### Admin Account
- **Email:** `admin@library.com`
- **Password:** `admin123`

### Member Accounts
- **Email:** `member@library.com` | **Password:** `member123`
- **Email:** `jane@library.com` | **Password:** `jane123`

## 🎯 Frontend Integration

This backend is **100% compatible** with your existing Angular 20 frontend:

✅ All API routes use `/api/*` prefix  
✅ Response formats match frontend expectations exactly  
✅ Field names use camelCase as expected by Angular  
✅ JWT authentication works seamlessly  
✅ CORS configured for `localhost:4200`

**Just run your Angular frontend and it will work immediately!**

## 🏗 Development

### Adding New Routes
1. Create a new blueprint in `routes/` directory
2. Register it in `gateway.py`
3. Add any new models/schemas as needed

### Database Management
- **SQLAlchemy ORM** for new features
- **Legacy SQLite** maintained for backward compatibility
- **Automatic migration** support via Flask-Migrate

### Testing
```bash
# Test the gateway structure
python test_gateway.py

# Run the application
python gateway.py
```

## 📦 Production Setup

For production deployment:

1. Update database URI in `config.py`
2. Set environment variables for `SECRET_KEY` and `JWT_SECRET_KEY`
3. Use a production WSGI server like Gunicorn:

```bash
gunicorn gateway:create_app()
```

## 🔄 Migration from Old Structure

The new gateway structure maintains **100% backward compatibility**:

- **Old routes** still work via legacy blueprints
- **Existing database** continues to function
- **Frontend** requires no changes
- **Gradual migration** to new structure possible

## 🎉 Benefits of New Structure

1. **Modularity** - Routes organized by functionality
2. **Maintainability** - Easier to add new features
3. **Testing** - Better separation of concerns
4. **Scalability** - Blueprint-based architecture
5. **Compatibility** - No breaking changes

---

**Your Library Management System is now powered by a modern, scalable API Gateway! 🚀**
