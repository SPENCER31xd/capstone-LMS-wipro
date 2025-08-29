import subprocess
import sys
import time
import os

def start_services():
    """Start both Flask backend and Angular frontend"""
    
    print("🚀 Starting Library Management System Services")
    print("=" * 60)
    
    # Start Flask backend
    print("\n📍 Starting Flask Backend...")
    backend_process = subprocess.Popen(
        [sys.executable, "corrected_app.py"],
        cwd="backend",
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
    )
    
    # Wait a bit for backend to start
    time.sleep(3)
    
    # Start Angular frontend
    print("📍 Starting Angular Frontend...")
    frontend_process = subprocess.Popen(
        ["ng", "serve", "--open"],
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
    )
    
    print("\n✅ Services started!")
    print("🔗 Backend: Running on port 5000")
    print("🔗 Frontend: Running on port 4200")
    print("\n🔑 Login credentials:")
    print("   Admin: admin@library.com / admin123")
    print("   Member: member@library.com / member123")
    print("\n⚠️  Press Ctrl+C to stop all services")
    
    try:
        # Keep script running
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ Services stopped!")

if __name__ == "__main__":
    start_services()
