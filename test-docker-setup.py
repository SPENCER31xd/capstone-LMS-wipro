#!/usr/bin/env python3
"""
Docker Setup Test Script
This script helps diagnose Docker Compose issues
"""

import subprocess
import sys
import os
import time

def run_command(command, check=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"❌ Command failed: {command}")
            print(f"Error: {result.stderr}")
            return False
        return result
    except Exception as e:
        print(f"❌ Error running command '{command}': {e}")
        return False

def check_docker():
    """Check if Docker is available and running"""
    print("🔍 Checking Docker installation...")
    
    # Check Docker version
    result = run_command("docker --version", check=False)
    if not result or result.returncode != 0:
        print("❌ Docker is not installed or not accessible")
        return False
    
    print(f"✅ Docker version: {result.stdout.strip()}")
    
    # Check if Docker daemon is running
    result = run_command("docker info", check=False)
    if not result or result.returncode != 0:
        print("❌ Docker daemon is not running")
        print("   Please start Docker Desktop")
        return False
    
    print("✅ Docker daemon is running")
    return True

def check_docker_compose():
    """Check if Docker Compose is available"""
    print("\n🔍 Checking Docker Compose...")
    
    result = run_command("docker-compose --version", check=False)
    if not result or result.returncode != 0:
        print("❌ Docker Compose is not available")
        return False
    
    print(f"✅ Docker Compose version: {result.stdout.strip()}")
    return True

def check_ports():
    """Check if required ports are available"""
    print("\n🔍 Checking port availability...")
    
    # Check port 80
    result = run_command("netstat -an | findstr :80", check=False)
    if result and result.stdout.strip():
        print("⚠️  Port 80 is in use:")
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                print(f"   {line.strip()}")
    else:
        print("✅ Port 80 is available")
    
    # Check port 5000
    result = run_command("netstat -an | findstr :5000", check=False)
    if result and result.stdout.strip():
        print("⚠️  Port 5000 is in use:")
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                print(f"   {line.strip()}")
    else:
        print("✅ Port 5000 is available")

def check_files():
    """Check if required files exist"""
    print("\n🔍 Checking required files...")
    
    required_files = [
        "docker-compose.yml",
        "Dockerfile.backend",
        "Dockerfile.frontend",
        "backend/app.py",
        "backend/requirements.txt",
        "package.json"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING!")

def check_database():
    """Check if database file exists"""
    print("\n🔍 Checking database file...")
    
    db_path = "backend/library.db"
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"✅ Database exists: {db_path} ({size} bytes)")
    else:
        print(f"⚠️  Database not found: {db_path}")
        print("   This will be created automatically by Docker")

def test_docker_build():
    """Test Docker build process"""
    print("\n🔍 Testing Docker build...")
    
    print("Building backend image...")
    result = run_command("docker build -f Dockerfile.backend -t library-backend-test .", check=False)
    if result and result.returncode == 0:
        print("✅ Backend image built successfully")
    else:
        print("❌ Backend image build failed")
        return False
    
    print("Building frontend image...")
    result = run_command("docker build -f Dockerfile.frontend -t library-frontend-test .", check=False)
    if result and result.returncode == 0:
        print("✅ Frontend image built successfully")
    else:
        print("❌ Frontend image build failed")
        return False
    
    return True

def cleanup_test_images():
    """Clean up test images"""
    print("\n🧹 Cleaning up test images...")
    run_command("docker rmi library-backend-test library-frontend-test", check=False)

def main():
    """Main function"""
    print("=" * 60)
    print("Docker Setup Test Script")
    print("=" * 60)
    
    # Check prerequisites
    if not check_docker():
        print("\n❌ Docker is not ready. Please fix Docker issues first.")
        return
    
    if not check_docker_compose():
        print("\n❌ Docker Compose is not ready. Please fix Docker Compose issues first.")
        return
    
    # Check environment
    check_ports()
    check_files()
    check_database()
    
    # Test Docker build
    print("\n" + "=" * 60)
    print("Testing Docker Build Process")
    print("=" * 60)
    
    if test_docker_build():
        print("\n✅ Docker build test passed!")
        print("\n🎯 Your Docker setup is ready!")
        print("\nNext steps:")
        print("1. Run: docker-compose up --build")
        print("2. Access frontend at: http://localhost")
        print("3. Access backend at: http://localhost:5000")
    else:
        print("\n❌ Docker build test failed!")
        print("\nTroubleshooting:")
        print("1. Check the error messages above")
        print("2. Ensure all required files exist")
        print("3. Check Docker Desktop logs")
        print("4. Try: docker system prune -a")
    
    # Cleanup
    cleanup_test_images()
    
    print("\n" + "=" * 60)
    print("Test completed!")

if __name__ == "__main__":
    main()
