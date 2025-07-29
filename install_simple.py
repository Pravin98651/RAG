#!/usr/bin/env python3
"""
Simple installation script for Insurance Policy RAG System
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

def install_packages_individual():
    """Install packages individually to avoid conflicts"""
    print("\n=== Installing Packages Individually ===")
    
    packages = [
        ("pypdf2", "PDF processing"),
        ("pdfplumber", "Advanced PDF processing"),
        ("sentence-transformers", "Text embeddings"),
        ("chromadb", "Vector database"),
        ("numpy", "Numerical computing"),
        ("pandas", "Data manipulation"),
        ("nltk", "Natural language processing"),
        ("spacy", "Advanced NLP")
    ]
    
    for package, description in packages:
        if not run_command(f"pip install {package}", f"Installing {package} ({description})"):
            print(f"Warning: Failed to install {package}")
            continue

def download_models():
    """Download required NLP models"""
    print("\n=== Downloading Models ===")
    
    # Download spaCy model
    if not run_command("python -m spacy download en_core_web_sm", "Downloading spaCy English model"):
        print("Warning: spaCy model download failed")
    
    # Download NLTK data
    nltk_commands = [
        "python -c \"import nltk; nltk.download('punkt')\"",
        "python -c \"import nltk; nltk.download('stopwords')\""
    ]
    
    for cmd in nltk_commands:
        if not run_command(cmd, "Downloading NLTK data"):
            print("Warning: NLTK data download failed")

def create_directories():
    """Create necessary directories"""
    print("\n=== Creating Directories ===")
    
    directories = [
        "vector_db",
        "logs",
        "reports"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ Created directory: {directory}")
        else:
            print(f"✓ Directory already exists: {directory}")

def test_imports():
    """Test if essential imports work"""
    print("\n=== Testing Essential Imports ===")
    
    essential_imports = [
        ("pypdf2", "PyPDF2"),
        ("pdfplumber", "PDFPlumber"),
        ("sentence_transformers", "Sentence Transformers"),
        ("chromadb", "ChromaDB"),
        ("numpy", "NumPy"),
        ("pandas", "Pandas"),
        ("nltk", "NLTK")
    ]
    
    all_working = True
    for module, name in essential_imports:
        try:
            __import__(module)
            print(f"✓ {name} imported successfully")
        except ImportError as e:
            print(f"✗ {name} import failed: {e}")
            all_working = False
    
    # Test spaCy
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✓ spaCy model loaded successfully")
    except Exception as e:
        print(f"✗ spaCy model loading failed: {e}")
        all_working = False
    
    return all_working

def main():
    """Main installation function"""
    print("Insurance Policy RAG System - Simple Installation")
    print("=" * 50)
    
    # Install packages individually
    install_packages_individual()
    
    # Download models
    download_models()
    
    # Create directories
    create_directories()
    
    # Test imports
    if test_imports():
        print("\n" + "=" * 50)
        print("✓ Installation completed successfully!")
        print("\nNext steps:")
        print("1. Place your PDF files in the 'Training_pdfs' directory")
        print("2. Run: python insurance_rag_simple.py")
        print("3. Or run: python demo_simple.py")
    else:
        print("\n" + "=" * 50)
        print("⚠ Installation completed with warnings")
        print("Some packages may not be working correctly.")
        print("Try running the simple version: python insurance_rag_simple.py")

if __name__ == "__main__":
    main() 