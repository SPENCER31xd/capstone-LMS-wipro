@echo off
REM Library Management System - Quick Start Script for Windows
REM This script sets up and runs the Flask backend

echo ==========================================
echo Library Management System - Backend Setup
echo ==========================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH. Please install Python and try again.
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: pip is not installed or not in PATH. Please install pip and try again.
    pause
    exit /b 1
)

echo Installing Python dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies. Please check the error messages above.
    pause
    exit /b 1
)

echo Dependencies installed successfully!
echo.

echo Setting up database and seeding data...
python seed_data.py

echo.
echo ==========================================
echo Setup completed successfully!
echo ==========================================
echo.
echo Starting Flask application...
echo API will be available at: http://localhost:8000
echo.
echo Default admin login:
echo   Email: admin@library.com
echo   Password: admin123
echo.
echo Press Ctrl+C to stop the server
echo ==========================================

REM Run the Flask application
python app.py
