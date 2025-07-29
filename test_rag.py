#!/usr/bin/env python3
"""
Simple test script for the RAG system
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import pypdf
        print("✓ PyPDF imported successfully")
    except ImportError as e:
        print(f"✗ PyPDF import failed: {e}")
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
        import nltk
        nltk.data.find('tokenizers/punkt')
        print("✓ NLTK data available")
    except LookupError:
        print("✗ NLTK data not found")
        return False
    
    return True

def test_pdf_processing():
    """Test PDF processing capabilities"""
    print("\nTesting PDF processing...")
    
    pdf_dir = Path("./Training_pdfs")
    if not pdf_dir.exists():
        print("✗ Training_pdfs directory not found")
        return False
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        print("✗ No PDF files found in Training_pdfs directory")
        return False
    
    print(f"✓ Found {len(pdf_files)} PDF files")
    
    # Test processing one PDF
    try:
        import pdfplumber
        with pdfplumber.open(pdf_files[0]) as pdf:
            text = pdf.pages[0].extract_text()
            if text:
                print(f"✓ Successfully extracted text from {pdf_files[0].name}")
                return True
            else:
                print(f"✗ No text extracted from {pdf_files[0].name}")
                return False
    except Exception as e:
        print(f"✗ Error processing PDF: {e}")
        return False

def test_rag_system():
    """Test the RAG system"""
    print("\nTesting RAG system...")
    
    try:
        from insurance_rag_no_spacy import InsuranceRAGSystem
        
        # Initialize system
        rag_system = InsuranceRAGSystem("./Training_pdfs")
        print("✓ RAG system initialized successfully")
        
        # Get statistics
        stats = rag_system.get_statistics()
        print(f"✓ System statistics: {stats['total_documents']} documents, {stats['total_chunks']} chunks")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing RAG system: {e}")
        return False

def main():
    """Main test function"""
    print("Insurance Policy RAG System - Test")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        print("\n✗ Import tests failed")
        return
    
    # Test PDF processing
    if not test_pdf_processing():
        print("\n✗ PDF processing tests failed")
        return
    
    # Test RAG system
    if not test_rag_system():
        print("\n✗ RAG system tests failed")
        return
    
    print("\n" + "=" * 40)
    print("✓ All tests passed!")
    print("\nThe RAG system is ready to use.")
    print("Run: python insurance_rag_no_spacy.py")

if __name__ == "__main__":
    main() 