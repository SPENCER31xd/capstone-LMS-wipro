@echo off
echo 🚀 Starting Library Management System
echo =====================================

echo 📍 Starting Flask Backend...
cd backend
start "Flask Backend" python corrected_app.py

echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo 📍 Starting Angular Frontend...
cd ..
start "Angular Frontend" ng serve --open

echo ✅ Both services started!
echo 🔗 Backend: http://localhost:5000
echo 🔗 Frontend: http://localhost:4200
echo.
echo 🔑 Login credentials:
echo    Admin: admin@library.com / admin123
echo    Member: member@library.com / member123
echo.
echo ⚠️  Keep both windows open to maintain the services
pause
