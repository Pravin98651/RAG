#!/usr/bin/env python3
"""
Test script to verify vector database connection and data
"""

import os
import sys
from pathlib import Path
import chromadb

def test_vector_db_connection():
    """Test direct connection to vector database"""
    print("Testing vector database connection...")
    
    try:
        # Check if vector_db directory exists
        vector_db_path = Path("./vector_db")
        if not vector_db_path.exists():
            print("✗ Vector database directory not found")
            return False
        
        print(f"✓ Vector database directory exists: {vector_db_path}")
        
        # Check ChromaDB files
        chroma_files = list(vector_db_path.glob("*"))
        print(f"✓ Found {len(chroma_files)} files in vector database")
        
        for file in chroma_files:
            if file.is_file():
                size_mb = file.stat().st_size / (1024 * 1024)
                print(f"  - {file.name}: {size_mb:.2f} MB")
            else:
                print(f"  - {file.name}/ (directory)")
        
        # Try to connect to ChromaDB
        client = chromadb.PersistentClient(path=str(vector_db_path))
        print("✓ ChromaDB client created successfully")
        
        # Try to get collection
        collection = client.get_or_create_collection("insurance_policies")
        print("✓ Collection accessed successfully")
        
        # Check collection data
        try:
            data = collection.get()
            total_chunks = len(data['ids']) if data['ids'] else 0
            print(f"✓ Collection has {total_chunks} chunks")
            
            if total_chunks > 0:
                print("✓ Vector database has data!")
                
                # Show some metadata
                if data['metadatas']:
                    source_files = set()
                    for metadata in data['metadatas']:
                        if metadata and 'source_file' in metadata:
                            source_files.add(metadata['source_file'])
                    
                    print(f"✓ Source files: {list(source_files)}")
                
                return True
            else:
                print("⚠️ Collection is empty")
                return False
                
        except Exception as e:
            print(f"✗ Error reading collection data: {e}")
            return False
            
    except Exception as e:
        print(f"✗ Error connecting to vector database: {e}")
        return False

def test_rag_system():
    """Test RAG system with vector database"""
    print("\nTesting RAG system...")
    
    try:
        from insurance_rag_no_spacy import InsuranceRAGSystem
        
        # Initialize RAG system
        rag_system = InsuranceRAGSystem("./Training_pdfs")
        print("✓ RAG system initialized")
        
        # Check if it has data
        if rag_system.has_data():
            print("✓ RAG system has data")
            
            # Get statistics
            stats = rag_system.get_statistics()
            print(f"✓ Statistics: {stats['total_chunks']} chunks, {stats['total_documents']} documents")
            
            # Test a simple query
            try:
                results = rag_system.query("test", top_k=1)
                print(f"✓ Query test successful: {len(results)} results")
                return True
            except Exception as e:
                print(f"✗ Query test failed: {e}")
                return False
        else:
            print("✗ RAG system has no data")
            return False
            
    except Exception as e:
        print(f"✗ Error testing RAG system: {e}")
        return False

def main():
    """Main test function"""
    print("Vector Database Test")
    print("=" * 40)
    
    # Test vector database connection
    db_ok = test_vector_db_connection()
    
    if not db_ok:
        print("\n✗ Vector database test failed")
        return
    
    # Test RAG system
    rag_ok = test_rag_system()
    
    print("\n" + "=" * 40)
    if db_ok and rag_ok:
        print("✓ All tests passed! Vector database is working correctly.")
    else:
        print("✗ Some tests failed. Check the vector database.")

if __name__ == "__main__":
    main() 