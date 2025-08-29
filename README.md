# 📚 Library Management System - Full Stack

A complete **Angular 20 + Flask + SQLite** Library Management System with JWT authentication, role-based access control, and modern UI.

## ✨ Features

### 🔐 **Authentication & Authorization**
- JWT-based authentication with secure token management
- Role-based access: **Admin** and **Member** with different privileges
- Account status management (active/blocked users)

### 👑 **Admin Features**
- **📖 Book Management**: Add, edit, delete, and view all books
- **👥 User Management**: View all members, block/unblock accounts
- **📊 Transaction Oversight**: Monitor all borrowing/returning activities
- **📈 Dashboard Analytics**: View system statistics and reports

### 👤 **Member Features** 
- **🔍 Browse Books**: Search and filter available books by category/author
- **📖 Borrow Books**: Request books with automatic due date calculation
- **↩️ Return Books**: Return borrowed books and view transaction history
- **📋 Personal Dashboard**: Track borrowed books and due dates

### 🛠 **Technical Stack**
- **Frontend**: Angular 20 with Angular Material UI
- **Backend**: Flask with RESTful API architecture
- **Database**: SQLite with proper relational schema
- **Authentication**: JWT tokens with secure validation
- **CORS**: Properly configured for cross-origin requests

## 🚀 **Quick Start**

### **Option 1: Automated Start (Recommended)**

**Windows:**
```bash
start-project.bat
```

**Linux/Mac:**
   ```bash
chmod +x start-project.sh
./start-project.sh
   ```

### **Option 2: Manual Start**

**Terminal 1 - Start Backend:**
   ```bash
cd backend
pip install Flask Flask-CORS Flask-JWT-Extended Werkzeug
python app.py
   ```

**Terminal 2 - Start Frontend:**
   ```bash
   ng serve
   ```

## 🌐 **Access URLs**

- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:5000
- **API Documentation**: All endpoints listed below

## 🔑 **Login Credentials**

### **Admin Account**
- **Email**: `admin@library.com`
- **Password**: `admin123`
- **Privileges**: Full system access, user management, book management

### **Member Accounts**
- **Email**: `member@library.com` | **Password**: `member123`
- **Email**: `jane@library.com` | **Password**: `jane123`
- **Privileges**: Browse books, borrow/return, view personal transactions

## 📋 **API Endpoints**

### **🔐 Authentication**
```http
POST /api/login       # User login
POST /api/signup      # User registration
```

### **📚 Books Management**
```http
GET    /api/books           # Get all books
GET    /api/books/{id}      # Get specific book
POST   /api/books           # Create book (Admin only)
PUT    /api/books/{id}      # Update book (Admin only) 
DELETE /api/books/{id}      # Delete book (Admin only)
```

### **📖 Book Transactions**
```http
GET  /api/transactions           # Get user transactions (all for admin)
POST /api/borrow/{book_id}       # Borrow a book
POST /api/return/{transaction_id} # Return a book
```

### **👥 Member Management (Admin Only)**
```http
GET /api/members           # Get all members
PUT /api/members/{id}      # Update member status (block/unblock)
```

## 💾 **Database Schema**

### **Users Table**
- `id`, `email`, `password`, `firstName`, `lastName`, `role`, `isActive`, `createdAt`

### **Books Table** 
- `id`, `title`, `author`, `isbn`, `category`, `publishedYear`, `description`
- `totalCopies`, `availableCopies`, `imageUrl`, `createdAt`, `updatedAt`

### **Transactions Table**
- `id`, `bookId`, `userId`, `type`, `issueDate`, `dueDate`, `returnDate`
- `status`, `fine`, `createdAt`, `updatedAt`

## 🎯 **Business Rules**

### **📖 Borrowing System**
- Members can borrow **maximum 5 books** simultaneously
- Default loan period: **14 days**
- **Automatic fine calculation**: $1 per day for overdue books
- Cannot borrow the same book twice while active
- Book availability updates automatically

### **👑 Admin Privileges**
- Complete system oversight and management
- Can manage all books and user accounts
- View all transactions and generate reports
- Block/unblock member accounts

### **🔒 Security Features**
- JWT token-based authentication
- Password hashing with Werkzeug
- CORS protection configured for Angular frontend
- Role-based route protection

## 📊 **Pre-loaded Sample Data**

### **📚 Books Available**
- The Great Gatsby by F. Scott Fitzgerald
- To Kill a Mockingbird by Harper Lee  
- Clean Code by Robert C. Martin
- Sapiens by Yuval Noah Harari
- The Lean Startup by Eric Ries
- **Do bailo ki gatha by prem chand** ⭐ (Your custom book!)

### **👥 Sample Users**
- 1 Admin account for system management
- 2 Member accounts for testing borrowing features
- Pre-configured with sample transaction history

## 🔧 **Development**

### **Frontend Development**
```bash
ng serve                # Development server
ng build               # Production build  
ng test                # Run unit tests
ng e2e                 # Run e2e tests
```

### **Backend Development**
```bash
python app.py          # Start Flask development server
# Database is automatically created and seeded
```

### **Project Structure**
```
library-management/
├── src/                    # Angular frontend
│   ├── app/
│   │   ├── models/         # TypeScript interfaces
│   │   ├── services/       # API service layer
│   │   ├── modules/        # Feature modules (auth, admin, member)
│   │   └── shared/         # Shared components
├── backend/                # Flask backend
│   ├── app.py              # Main Flask application
│   ├── auth_routes.py      # Authentication endpoints
│   ├── book_routes.py      # Book management endpoints
│   ├── transaction_routes.py # Transaction endpoints
│   ├── member_routes.py    # Member management endpoints
│   └── library.db          # SQLite database (auto-created)
├── start-project.bat       # Windows startup script
├── start-project.sh        # Linux/Mac startup script
└── README.md               # This file
```

## 🐛 **Troubleshooting**

### **Common Issues**

1. **Backend won't start**: Make sure Flask dependencies are installed
   ```bash
   pip install Flask Flask-CORS Flask-JWT-Extended Werkzeug
   ```

2. **Frontend won't compile**: Check Angular dependencies
   ```bash
   npm install
   ```

3. **CORS errors**: Ensure backend is running on port 5000
4. **Login fails**: Check that backend database is initialized (happens automatically)
5. **Books don't load**: Ensure you're logged in with valid JWT token

### **Resetting Database**
Delete `backend/library.db` and restart the backend - it will recreate with seed data.

## 🎉 **Ready to Use!**

Your Library Management System is now **fully functional**! 

🎯 **Next Steps:**
1. Run the startup script or start both servers manually
2. Open http://localhost:4200 in your browser  
3. Login with admin credentials to explore all features
4. Try borrowing "Do bailo ki gatha" as a member!

**Enjoy your complete full-stack Library Management System!** 📚✨