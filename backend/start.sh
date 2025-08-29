#!/bin/bash

# Library Management System - Quick Start Script
# This script sets up and runs the Flask backend

echo "=========================================="
echo "Library Management System - Backend Setup"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed. Please install pip3 and try again."
    exit 1
fi

echo "Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies. Please check the error messages above."
    exit 1
fi

echo "Dependencies installed successfully!"
echo ""

echo "Setting up database and seeding data..."
python3 seed_data.py

echo ""
echo "=========================================="
echo "Setup completed successfully!"
echo "=========================================="
echo ""
echo "Starting Flask application..."
echo "API will be available at: http://localhost:8000"
echo ""
echo "Default admin login:"
echo "  Email: admin@library.com"
echo "  Password: admin123"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="

# Run the Flask application
python3 app.py
