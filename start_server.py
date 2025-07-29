#!/usr/bin/env python3
"""
Startup script for Insurance Policy RAG API
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if all dependencies are installed"""
    print("Checking dependencies...")
    
    required_modules = [
        "fastapi",
        "uvicorn", 
        "httpx",
        "pydantic",
        "loguru",
        "dotenv"
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError:
            print(f"✗ {module} - missing")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\nMissing modules: {', '.join(missing_modules)}")
        print("Install with: pip install -r requirements_api.txt")
        return False
    
    return True

def check_environment():
    """Check environment setup"""
    print("\nChecking environment...")
    
    # Check .env file
    if not Path(".env").exists():
        print("✗ .env file not found")
        print("Run: python setup_env.py")
        return False
    
    # Check vector database
    if not Path("vector_db").exists():
        print("✗ Vector database not found")
        return False
    
    print("✓ Environment ready")
    return True

def start_server():
    """Start the API server"""
    print("\nStarting API server...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Start uvicorn server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "api_backend:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")

def main():
    """Main startup function"""
    print("Insurance Policy RAG API - Server Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\nDependency check failed. Please install missing packages.")
        return
    
    # Check environment
    if not check_environment():
        print("\nEnvironment check failed. Please fix the issues above.")
        return
    
    # Start server
    start_server()

if __name__ == "__main__":
    main() 