# 🐳 Library Management System - Docker Containerization

This document explains how to containerize and run your Library Management System using Docker without changing any existing code.

## 📋 Prerequisites

- **Docker Desktop** installed and running
- **Docker Compose** (usually comes with Docker Desktop)
- **Git** (for cloning the repository)

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Nginx         │
│   (Angular)     │    │   (Flask)       │    │   (Reverse     │
│   Port: 80      │◄──►│   Port: 5000    │◄──►│   Proxy)       │
│                 │    │                 │    │   Port: 80      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 1. **Start Everything (Recommended)**
```bash
# Windows
start-docker.bat

# Linux/Mac
./start-docker.sh
```

### 2. **Manual Start**
```bash
# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

## 🌐 Access Points

- **Frontend Application**: http://localhost
- **Backend API**: http://localhost/api
- **Health Check**: http://localhost/health

## 📁 File Structure

```
project-root/
├── Dockerfile.frontend          # Angular frontend container
├── Dockerfile.backend           # Flask backend container
├── docker-compose.yml           # Main compose file
├── docker-compose.override.yml  # Development overrides
├── docker-compose.prod.yml      # Production overrides
├── nginx.conf                   # Nginx reverse proxy config
├── .dockerignore                # Docker build exclusions
├── env.example                  # Environment variables template
├── start-docker.sh             # Linux/Mac startup script
├── start-docker.bat            # Windows startup script
├── backend/                     # Your existing backend code
├── src/                        # Your existing Angular source
└── logs/                       # Application logs
```

## 🔧 Configuration

### Environment Variables
Copy `env.example` to `.env` and customize:
```bash
cp env.example .env
```

### Database Persistence
The SQLite database file (`backend/library.db`) is mounted as a volume, so your data persists between container restarts.

### CORS Configuration
CORS is handled automatically by the Nginx reverse proxy. No changes needed in your Flask or Angular code.

## 🐛 Troubleshooting

### Common Issues

#### 1. **Port Already in Use**
```bash
# Check what's using port 80
netstat -ano | findstr :80  # Windows
lsof -i :80                 # Linux/Mac

# Stop conflicting services or change ports in docker-compose.yml
```

#### 2. **Database Permission Issues**
```bash
# Set proper permissions (Linux/Mac)
chmod 666 backend/library.db

# Windows: Ensure Docker has access to the file
```

#### 3. **Container Won't Start**
```bash
# Check logs
docker-compose logs [service-name]

# Rebuild containers
docker-compose down
docker-compose up --build
```

#### 4. **Frontend Not Loading**
```bash
# Check if Angular build succeeded
docker-compose logs frontend

# Verify nginx configuration
docker-compose exec nginx nginx -t
```

### Health Checks
```bash
# Check all services
docker-compose ps

# Individual service health
curl http://localhost/health          # Nginx
curl http://localhost:5000/api/books # Backend
```

## 🔄 Development vs Production

### Development Mode
```bash
# Uses docker-compose.override.yml automatically
docker-compose up --build

# Features:
# - Hot reload for both frontend and backend
# - Development ports (8080 for nginx)
# - Debug logging enabled
```

### Production Mode
```bash
# Use production configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Features:
# - Optimized builds
# - Resource limits
# - Production logging
# - SSL ready (add certificates to ./ssl/)
```

## 📊 Monitoring & Logs

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx

# Follow specific log file
docker-compose exec backend tail -f /app/logs/library_app.log
```

### Resource Usage
```bash
# Container resource usage
docker stats

# Detailed container info
docker-compose exec backend top
```

## 🔒 Security Features

- **Rate Limiting**: API endpoints are rate-limited
- **Security Headers**: XSS protection, frame options, etc.
- **CORS Handling**: Proper CORS configuration via Nginx
- **Health Checks**: Regular health monitoring
- **Resource Limits**: Memory and CPU constraints in production

## 🚀 Deployment

### Local Development
```bash
./start-docker.sh  # or start-docker.bat on Windows
```

### Production Server
```bash
# Copy files to server
scp -r . user@server:/path/to/app

# SSH to server and start
ssh user@server
cd /path/to/app
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### SSL/HTTPS
1. Add SSL certificates to `./ssl/` directory
2. Update nginx.conf with SSL configuration
3. Use production compose file

## 📝 Useful Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart specific service
docker-compose restart backend

# View running containers
docker-compose ps

# Execute command in container
docker-compose exec backend python manage.py shell

# View container logs
docker-compose logs -f [service]

# Rebuild specific service
docker-compose up --build [service]

# Clean up everything
docker-compose down -v --remove-orphans
docker system prune -f
```

## 🔍 Debugging

### Enter Container Shell
```bash
# Backend container
docker-compose exec backend bash

# Frontend container
docker-compose exec frontend sh

# Nginx container
docker-compose exec nginx sh
```

### Check Network
```bash
# List networks
docker network ls

# Inspect network
docker network inspect library-network
```

### Database Access
```bash
# Access SQLite database from host
sqlite3 backend/library.db

# From container
docker-compose exec backend sqlite3 /app/data/library.db
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Angular Documentation](https://angular.io/docs)

## 🤝 Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify Docker is running: `docker info`
3. Check service health: `docker-compose ps`
4. Review this troubleshooting guide
5. Check the main project README for application-specific issues

---

**Happy Containerizing! 🐳✨**

