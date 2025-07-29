#!/usr/bin/env python3
"""
Setup script for Insurance Policy RAG System
"""

import os
import sys
import subprocess
import platform

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

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher is required")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n=== Installing Dependencies ===")
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing Python packages"):
        return False
    
    return True

def download_models():
    """Download required NLP models"""
    print("\n=== Downloading Models ===")
    
    # Download spaCy model
    if not run_command("python -m spacy download en_core_web_sm", "Downloading spaCy English model"):
        return False
    
    # Download NLTK data
    nltk_commands = [
        "python -c \"import nltk; nltk.download('punkt')\"",
        "python -c \"import nltk; nltk.download('stopwords')\"",
        "python -c \"import nltk; nltk.download('averaged_perceptron_tagger')\""
    ]
    
    for cmd in nltk_commands:
        if not run_command(cmd, "Downloading NLTK data"):
            return False
    
    return True

def create_directories():
    """Create necessary directories"""
    print("\n=== Creating Directories ===")
    
    directories = [
        "vector_db",
        "logs",
        "reports",
        "data"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ Created directory: {directory}")
        else:
            print(f"✓ Directory already exists: {directory}")
    
    return True

def test_imports():
    """Test if all imports work correctly"""
    print("\n=== Testing Imports ===")
    
    try:
        import pypdf2
        print("✓ PyPDF2 imported successfully")
    except ImportError as e:
        print(f"✗ PyPDF2 import failed: {e}")
        return False
    
    try:
        import pdfplumber
        print("✓ PDFPlumber imported successfully")
    except ImportError as e:
        print(f"✗ PDFPlumber import failed: {e}")
        return False
    
    try:
        import sentence_transformers
        print("✓ Sentence Transformers imported successfully")
    except ImportError as e:
        print(f"✗ Sentence Transformers import failed: {e}")
        return False
    
    try:
        import chromadb
        print("✓ ChromaDB imported successfully")
    except ImportError as e:
        print(f"✗ ChromaDB import failed: {e}")
        return False
    
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✓ spaCy model loaded successfully")
    except Exception as e:
        print(f"✗ spaCy model loading failed: {e}")
        return False
    
    try:
        import nltk
        nltk.data.find('tokenizers/punkt')
        print("✓ NLTK data available")
    except LookupError:
        print("✗ NLTK data not found")
        return False
    
    return True

def main():
    """Main setup function"""
    print("Insurance Policy RAG System - Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n✗ Setup failed during dependency installation")
        sys.exit(1)
    
    # Download models
    if not download_models():
        print("\n✗ Setup failed during model download")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("\n✗ Setup failed during directory creation")
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("\n✗ Setup failed during import testing")
        sys.exit(1)
    
    print("\n" + "=" * 40)
    print("✓ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Place your PDF files in the 'Training_pdfs' directory")
    print("2. Run: python insurance_rag_system.py")
    print("3. Or run: python query_interface.py for interactive queries")
    print("4. Or run: python test_evaluation.py for comprehensive testing")

if __name__ == "__main__":
    main() 