#!/usr/bin/env python3
"""
Simple demo script for Insurance Policy RAG System
"""

import json
import time
from insurance_rag_simple import SimpleInsuranceRAGSystem

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
    if len(content) > 200:
        content = content[:200] + "..."
    print(f"   Content: {content}")

def demo_basic_queries(rag_system):
    """Demonstrate basic query capabilities"""
    print_header("BASIC QUERY DEMONSTRATION")
    
    demo_queries = [
        "What are the coverage limits?",
        "What is excluded from coverage?",
        "How much is the premium?",
        "What are the claim procedures?",
        "What are the policy terms and conditions?"
    ]
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n--- Query {i}: {query} ---")
        
        start_time = time.time()
        results = rag_system.query(query, top_k=3)
        query_time = time.time() - start_time
        
        if results:
            print(f"Found {len(results)} results in {query_time:.2f} seconds")
            for j, result in enumerate(results, 1):
                print_result(result, j)
        else:
            print("No relevant results found.")
        
        print("-" * 40)

def demo_filtered_queries(rag_system):
    """Demonstrate filtered query capabilities"""
    print_header("FILTERED QUERY DEMONSTRATION")
    
    # Filter by section type
    print("\n--- Filtering by Section Type ---")
    results = rag_system.query(
        "What is covered?",
        filter_metadata={"section_type": "coverage"}
    )
    
    if results:
        print(f"Found {len(results)} coverage-related results")
        for i, result in enumerate(results[:2], 1):
            print_result(result, i)
    else:
        print("No coverage-related results found.")
    
    # Filter by source file
    print("\n--- Filtering by Source File ---")
    stats = rag_system.get_statistics()
    if stats['processed_files']:
        first_file = stats['processed_files'][0]
        results = rag_system.query(
            "Premium amount",
            filter_metadata={"source_file": first_file}
        )
        
        if results:
            print(f"Found {len(results)} results from {first_file}")
            for i, result in enumerate(results[:2], 1):
                print_result(result, i)
        else:
            print(f"No results found in {first_file}")

def demo_system_statistics(rag_system):
    """Demonstrate system statistics"""
    print_header("SYSTEM STATISTICS")
    
    stats = rag_system.get_statistics()
    
    print(f"Total Documents Processed: {stats['total_documents']}")
    print(f"Total Chunks Created: {stats['total_chunks']}")
    print(f"Vector Database Size: {stats['vector_db_size']}")
    
    print(f"\nProcessed Files:")
    for filename, file_stats in stats['file_statistics'].items():
        print(f"  📄 {filename}")
        print(f"     - Chunks: {file_stats['chunks']}")
        print(f"     - Pages: {file_stats['pages']}")
        print(f"     - Size: {file_stats['file_size_mb']:.2f} MB")

def demo_performance_metrics(rag_system):
    """Demonstrate performance metrics"""
    print_header("PERFORMANCE METRICS")
    
    # Test query performance
    test_queries = [
        "coverage limits",
        "exclusions",
        "premium payment",
        "claim process",
        "policy definitions"
    ]
    
    total_time = 0
    total_results = 0
    
    for query in test_queries:
        start_time = time.time()
        results = rag_system.query(query, top_k=3)
        query_time = time.time() - start_time
        
        total_time += query_time
        total_results += len(results) if results else 0
        
        print(f"Query: '{query}' - {len(results) if results else 0} results in {query_time:.3f}s")
    
    avg_time = total_time / len(test_queries)
    avg_results = total_results / len(test_queries)
    
    print(f"\nPerformance Summary:")
    print(f"  Average Query Time: {avg_time:.3f} seconds")
    print(f"  Average Results per Query: {avg_results:.1f}")
    print(f"  Total Processing Time: {total_time:.3f} seconds")

def interactive_demo(rag_system):
    """Interactive demo mode"""
    print_header("INTERACTIVE DEMO MODE")
    
    print("Starting interactive demo...")
    print("Type 'quit' to exit, 'stats' for statistics")
    
    while True:
        try:
            query = input("\nEnter your question: ").strip()
            
            if query.lower() == 'quit':
                break
            elif query.lower() == 'stats':
                demo_system_statistics(rag_system)
            else:
                print(f"\nSearching for: '{query}'")
                print("-" * 50)
                
                results = rag_system.query(query, top_k=5)
                
                if results:
                    for i, result in enumerate(results, 1):
                        print_result(result, i)
                else:
                    print("No relevant results found.")
                    
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main demo function"""
    print("Insurance Policy RAG System - Simple Demo")
    print("=" * 50)
    
    # Initialize RAG system
    print("Initializing RAG system...")
    rag_system = SimpleInsuranceRAGSystem("./Training_pdfs")
    
    # Check if documents are processed
    stats = rag_system.get_statistics()
    if stats['total_documents'] == 0:
        print("No documents processed. Processing PDFs...")
        rag_system.process_pdfs()
        print("Document processing completed!")
    
    # Run demos
    demo_system_statistics(rag_system)
    demo_basic_queries(rag_system)
    demo_filtered_queries(rag_system)
    demo_performance_metrics(rag_system)
    
    # Ask if user wants interactive demo
    print_header("DEMO COMPLETE")
    print("The demo has completed successfully!")
    print("\nWould you like to try the interactive query interface? (y/n)")
    
    try:
        response = input().strip().lower()
        if response in ['y', 'yes']:
            interactive_demo(rag_system)
    except KeyboardInterrupt:
        print("\nDemo ended.")
    
    print("\nThank you for trying the Insurance Policy RAG System!")

if __name__ == "__main__":
    main() 