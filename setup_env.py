#!/usr/bin/env python3
"""
Environment setup script for Insurance Policy RAG API
"""

import os
from pathlib import Path

def create_env_file():
    """Create .env file with proper configuration"""
    env_content = """# Insurance Policy RAG API Environment Variables

# Groq API Configuration
# Get your API key from: https://console.groq.com/
GROQ_API_KEY=your-groq-api-key-here

# API Authentication Token
API_TOKEN=c94dfd1ae12b50eb392cd6d1ef5f4578c561f54bacf6cd6849236cbfc2e8b673

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Logging Configuration
LOG_LEVEL=INFO
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✓ Created .env file")
        print("⚠️ Please update GROQ_API_KEY in .env file with your actual Groq API key")
        print("   Get your API key from: https://console.groq.com/")
    else:
        print("✓ .env file already exists")
    
    return True

def validate_env():
    """Validate environment variables"""
    print("\n=== Environment Validation ===")
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("✗ .env file not found")
        return False
    
    # Load and check variables
    from dotenv import load_dotenv
    load_dotenv()
    
    groq_key = os.getenv("GROQ_API_KEY")
    api_token = os.getenv("API_TOKEN")
    
    if not groq_key or groq_key == "your-groq-api-key-here":
        print("⚠️ GROQ_API_KEY not configured or using default value")
        print("   Please set your actual Groq API key in .env file")
    else:
        print("✓ GROQ_API_KEY configured")
    
    if api_token:
        print("✓ API_TOKEN configured")
    else:
        print("✗ API_TOKEN not configured")
    
    return True

def main():
    """Main setup function"""
    print("Insurance Policy RAG API - Environment Setup")
    print("=" * 50)
    
    # Create .env file
    create_env_file()
    
    # Validate environment
    validate_env()
    
    print("\n" + "=" * 50)
    print("✓ Environment setup completed!")
    print("\nNext steps:")
    print("1. Edit .env file and add your Groq API key")
    print("2. Start the API server: python api_backend.py")
    print("3. Test the API: python test_api_client.py")

if __name__ == "__main__":
    main() 