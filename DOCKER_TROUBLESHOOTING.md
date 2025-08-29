# Docker Troubleshooting Guide

If Docker Compose is not running properly, follow these steps to diagnose and fix the issue.

## Quick Start Commands

```bash
# Stop all containers and clean up
docker-compose down -v

# Remove all images and rebuild from scratch
docker system prune -a --volumes

# Rebuild and start
docker-compose up --build
```

## Common Issues and Solutions

### 1. Port Already in Use

**Error:** `Bind for 0.0.0.0:80 failed: port is already allocated`

**Solution:**
```bash
# Check what's using port 80
netstat -ano | findstr :80

# Kill the process using the port
taskkill /PID <PID> /F

# Or change the port in docker-compose.yml
ports:
  - "8080:80"  # Use port 8080 instead of 80
```

### 2. Database File Issues

**Error:** `Permission denied` or database not found

**Solution:**
```bash
# Ensure the database file exists
ls -la backend/library.db

# If it doesn't exist, create it
cd backend
python app.py
# This will create the database file
```

### 3. Docker Build Failures

**Error:** `Build failed` or `npm ci` fails

**Solution:**
```bash
# Clean Docker cache
docker system prune -a

# Check if you have enough disk space
docker system df

# Rebuild without cache
docker-compose build --no-cache
```

### 4. Frontend Build Issues

**Error:** Angular build fails

**Solution:**
```bash
# Check Node.js version (should be 18+)
node --version

# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### 5. Backend Import Errors

**Error:** `ModuleNotFoundError` or import issues

**Solution:**
```bash
# Check if all requirements are installed
cd backend
pip install -r requirements.txt

# Test the backend locally first
python app.py
```

## Step-by-Step Debugging

### Step 1: Test Backend Locally
```bash
cd backend
python app.py
```
If this fails, fix the backend issues first.

### Step 2: Test Frontend Locally
```bash
npm install
npm start
```
If this fails, fix the frontend issues first.

### Step 3: Test Docker Backend Only
```bash
# Comment out frontend service in docker-compose.yml
docker-compose up backend
```

### Step 4: Test Docker Frontend Only
```bash
# Comment out backend service in docker-compose.yml
docker-compose up frontend
```

## Environment Variables

Make sure these environment variables are set:

```bash
# Backend
FLASK_APP=app.py
FLASK_ENV=production
DATABASE=/app/data/library.db
JWT_SECRET_KEY=your-secret-key-change-in-production

# Frontend
NODE_ENV=production
```

## Logs and Debugging

### View Container Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f
```

### Check Container Status
```bash
docker-compose ps
docker-compose top
```

### Access Running Containers
```bash
# Backend container
docker exec -it library-backend /bin/bash

# Frontend container
docker exec -it library-frontend /bin/sh
```

## Network Issues

### Check Docker Networks
```bash
docker network ls
docker network inspect library-library-network
```

### Test Container Communication
```bash
# From frontend container
docker exec -it library-frontend wget -qO- http://localhost:5000/api/books

# From backend container
docker exec -it library-backend wget -qO- http://frontend:80
```

## File Permissions (Linux/Mac)

```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod -R 755 backend/
chmod 644 backend/library.db
```

## Windows-Specific Issues

### WSL2 Issues
```bash
# Restart WSL2
wsl --shutdown
wsl

# Restart Docker Desktop
```

### Path Issues
Ensure all paths use forward slashes or escaped backslashes in docker-compose.yml.

## Complete Reset

If nothing else works:

```bash
# Stop everything
docker-compose down -v
docker system prune -a --volumes

# Remove all containers and images
docker rm -f $(docker ps -aq)
docker rmi -f $(docker images -aq)

# Rebuild from scratch
docker-compose up --build
```

## Still Having Issues?

1. Check Docker Desktop logs
2. Ensure Docker Desktop is running
3. Try restarting Docker Desktop
4. Check Windows Defender Firewall
5. Ensure virtualization is enabled in BIOS
6. Update Docker Desktop to latest version

## Success Indicators

When everything is working:

✅ `docker-compose ps` shows both services as "Up"
✅ `http://localhost` loads the Angular app
✅ `http://localhost:5000/api/books` returns data
✅ Login/signup works without CORS errors
✅ No error messages in container logs

