#!/bin/bash

# Library Management System Docker Startup Script
# This script starts the entire application using Docker Compose

set -e

echo "🚀 Starting Library Management System..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs/nginx
mkdir -p data

# Set proper permissions for database file
if [ -f "backend/library.db" ]; then
    echo "🔒 Setting database file permissions..."
    chmod 666 backend/library.db
fi

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🏥 Checking service health..."
if docker-compose ps | grep -q "unhealthy"; then
    echo "⚠️  Some services are unhealthy. Check logs with: docker-compose logs"
else
    echo "✅ All services are healthy!"
fi

# Display service status
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "🎉 Library Management System is starting up!"
echo ""
echo "🌐 Access the application at: http://localhost"
echo "📚 API endpoints available at: http://localhost/api"
echo ""
echo "📋 Useful commands:"
echo "  View logs: docker-compose logs -f"
echo "  Stop services: docker-compose down"
echo "  Restart services: docker-compose restart"
echo "  View service status: docker-compose ps"
echo ""
echo "🔍 Default credentials:"
echo "  Admin: admin@library.com / admin123"
echo "  Member: member@library.com / member123"
echo "  Member: jane@library.com / jane123"

