#!/bin/bash

echo ""
echo "=========================================="
echo " Library Management System - Full Stack"
echo "=========================================="
echo ""

# Check if Flask dependencies are installed
echo "🔧 Checking Flask dependencies..."
cd backend
python -c "import flask, flask_cors, flask_jwt_extended" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing Flask dependencies..."
    pip install Flask Flask-CORS Flask-JWT-Extended Werkzeug
fi

# Start Flask backend
echo "🚀 Starting Flask Backend on Port 5000..."
python app.py &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 5

cd ..

# Start Angular frontend
echo "🌐 Starting Angular Frontend on Port 4200..."
ng serve --open &
FRONTEND_PID=$!

echo ""
echo "✅ Both servers are starting..."
echo ""
echo "🔗 URLs:"
echo "Backend:  http://localhost:5000"
echo "Frontend: http://localhost:4200"
echo ""
echo "🔑 Default credentials:"
echo "Admin:  admin@library.com / admin123"
echo "Member: member@library.com / member123"
echo ""
echo "📚 Your book 'Do bailo ki gatha by prem chand' is available!"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user to press Ctrl+C
trap "echo 'Stopping servers...; kill $BACKEND_PID $FRONTEND_PID; exit'" INT
wait


