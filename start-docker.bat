@echo off
echo ========================================
echo Library Management System - Docker Setup
echo ========================================
echo.

echo Checking Docker status...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not running!
    echo Please install Docker Desktop and ensure it's running.
    pause
    exit /b 1
)

echo Docker is available.
echo.

echo Stopping any existing containers...
docker-compose down

echo.
echo Building and starting services...
echo This may take a few minutes on first run...
echo.

docker-compose up --build

echo.
echo Services are running!
echo.
echo Frontend: http://localhost:4200
echo Gateway API: http://localhost:5000
echo.
echo Press any key to stop services...
pause >nul

echo Stopping services...
docker-compose down
echo Services stopped.

