#!/usr/bin/env python3
"""
Setup script for Insurance Policy RAG API
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def install_dependencies():
    """Install API dependencies"""
    print("\n=== Installing API Dependencies ===")
    
    if not run_command("pip install -r requirements_api.txt", "Installing API dependencies"):
        print("Failed to install API dependencies")
        return False
    
    return True

def setup_environment():
    """Setup environment variables"""
    print("\n=== Setting up Environment ===")
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write("# Insurance Policy RAG API Environment Variables\n")
            f.write("# Add your Groq API key here\n")
            f.write("GROQ_API_KEY=your-groq-api-key-here\n")
            f.write("\n# API Configuration\n")
            f.write("API_TOKEN=c94dfd1ae12b50eb392cd6d1ef5f4578c561f54bacf6cd6849236cbfc2e8b673\n")
        
        print("✓ Created .env file")
        print("⚠️ Please update GROQ_API_KEY in .env file with your actual Groq API key")
    else:
        print("✓ .env file already exists")
    
    return True

def test_imports():
    """Test if all required modules can be imported"""
    print("\n=== Testing API Imports ===")
    
    required_modules = [
        "fastapi",
        "uvicorn",
        "httpx",
        "pydantic",
        "loguru"
    ]
    
    all_working = True
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module} imported successfully")
        except ImportError as e:
            print(f"✗ {module} import failed: {e}")
            all_working = False
    
    return all_working

def create_directories():
    """Create necessary directories"""
    print("\n=== Creating Directories ===")
    
    directories = [
        "logs",
        "uploads",
        "temp"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ Created directory: {directory}")
        else:
            print(f"✓ Directory already exists: {directory}")

def main():
    """Main setup function"""
    print("Insurance Policy RAG API - Setup")
    print("=" * 50)
    
    # Install dependencies
    if not install_dependencies():
        print("\n✗ Setup failed during dependency installation")
        return
    
    # Setup environment
    if not setup_environment():
        print("\n✗ Setup failed during environment setup")
        return
    
    # Test imports
    if not test_imports():
        print("\n✗ Setup failed during import testing")
        return
    
    # Create directories
    create_directories()
    
    print("\n" + "=" * 50)
    print("✓ API setup completed successfully!")
    print("\nNext steps:")
    print("1. Update GROQ_API_KEY in .env file with your actual Groq API key")
    print("2. Start the API server: python api_backend.py")
    print("3. Test the API: python test_api_client.py")
    print("4. Access API documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    main() 