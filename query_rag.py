#!/usr/bin/env python3
"""
Simple query interface for the Insurance Policy RAG System
"""

import json
import time
from insurance_rag_no_spacy import InsuranceRAGSystem

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_result(result, index):
    """Print formatted result"""
    print(f"\n{index}. Similarity Score: {result['similarity_score']:.3f}")
    print(f"   Source: {result['metadata']['source_file']}")
    print(f"   Section: {result['metadata']['section_type']}")
    print(f"   Type: {result['metadata']['chunk_type']}")
    
    # Show content preview
    content = result['content']
    if len(content) > 300:
        content = content[:300] + "..."
    print(f"   Content: {content}")

def main():
    """Main query interface"""
    print("Insurance Policy RAG System - Query Interface")
    print("=" * 50)
    
    # Initialize RAG system
    print("Initializing RAG system...")
    rag_system = InsuranceRAGSystem("./Training_pdfs")
    
    # Check if documents are processed
    stats = rag_system.get_statistics()
    if stats['total_documents'] == 0:
        print("No documents processed. Processing PDFs...")
        rag_system.process_pdfs()
        print("Document processing completed!")
    
    # Show statistics
    print_header("SYSTEM STATISTICS")
    stats = rag_system.get_statistics()
    print(f"Total Documents: {stats['total_documents']}")
    print(f"Total Chunks: {stats['total_chunks']}")
    print(f"Vector DB Size: {stats['vector_db_size']}")
    
    # Example queries
    example_queries = [
        "What are the coverage limits?",
        "What is excluded from coverage?",
        "How much is the premium?",
        "What are the claim procedures?",
        "What are the policy terms and conditions?",
        "What is the waiting period?",
        "What are the benefits covered?",
        "What is the sum insured?",
        "What are the exclusions?",
        "How to file a claim?"
    ]
    
    print_header("EXAMPLE QUERIES")
    for i, query in enumerate(example_queries, 1):
        print(f"{i}. {query}")
    
    # Interactive query mode
    print_header("INTERACTIVE QUERY MODE")
    print("Type 'quit' to exit, 'stats' for statistics, 'examples' for example queries")
    
    while True:
        try:
            query = input("\nEnter your question: ").strip()
            
            if query.lower() == 'quit':
                break
            elif query.lower() == 'stats':
                stats = rag_system.get_statistics()
                print(f"\nTotal Documents: {stats['total_documents']}")
                print(f"Total Chunks: {stats['total_chunks']}")
                print(f"Vector DB Size: {stats['vector_db_size']}")
                continue
            elif query.lower() == 'examples':
                print("\nExample queries:")
                for i, q in enumerate(example_queries, 1):
                    print(f"{i}. {q}")
                continue
            elif not query:
                continue
            
            print(f"\nSearching for: '{query}'")
            print("-" * 50)
            
            start_time = time.time()
            results = rag_system.query(query, top_k=5)
            query_time = time.time() - start_time
            
            if results:
                print(f"Found {len(results)} results in {query_time:.2f} seconds")
                for i, result in enumerate(results, 1):
                    print_result(result, i)
            else:
                print("No relevant results found.")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nThank you for using the Insurance Policy RAG System!")

if __name__ == "__main__":
    main() 