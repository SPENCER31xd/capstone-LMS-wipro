@echo off
echo.
echo ==========================================
echo  Library Management System - Full Stack
echo ==========================================
echo.
echo Starting Flask Backend on Port 5000...
echo Starting Angular Frontend on Port 4200...
echo.

REM Start Flask backend in new window
start "Flask Backend" cmd /c "cd backend && python app.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak > nul

REM Start Angular frontend in new window  
start "Angular Frontend" cmd /c "ng serve --open"

echo.
echo Backend: http://localhost:5000
echo Frontend: http://localhost:4200 (will open automatically)
echo.
echo Default credentials:
echo Admin: admin@library.com / admin123
echo Member: member@library.com / member123
echo.
echo Your book "Do bailo ki gatha" is available in the system!
echo.
pause


