import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
from insurance_rag_system import InsuranceRAGSystem

class InsuranceQueryInterface:
    """
    Interactive query interface for insurance policy RAG system
    """
    
    def __init__(self, rag_system: InsuranceRAGSystem):
        self.rag_system = rag_system
        self.query_history = []
        
    def interactive_query(self) -> None:
        """Interactive query interface"""
        print("=== Insurance Policy RAG System ===")
        print("Type 'quit' to exit, 'help' for commands, 'stats' for statistics")
        
        while True:
            try:
                query = input("\nEnter your question: ").strip()
                
                if query.lower() == 'quit':
                    break
                elif query.lower() == 'help':
                    self._show_help()
                elif query.lower() == 'stats':
                    self._show_statistics()
                elif query.lower() == 'history':
                    self._show_query_history()
                elif query.lower() == 'filter':
                    self._show_filter_options()
                elif query.lower().startswith('filter:'):
                    self._handle_filtered_query(query[7:])
                else:
                    self._process_query(query)
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def _process_query(self, query: str, top_k: int = 5, filter_metadata: Optional[Dict] = None) -> None:
        """Process a query and display results"""
        print(f"\nSearching for: '{query}'")
        print("-" * 50)
        
        # Record query
        query_record = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'filter': filter_metadata
        }
        
        # Get results
        results = self.rag_system.query(query, top_k=top_k, filter_metadata=filter_metadata)
        
        if not results:
            print("No relevant results found.")
            return
        
        # Display results
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Similarity Score: {result['similarity_score']:.3f}")
            print(f"   Source: {result['metadata']['source_file']}")
            print(f"   Section: {result['metadata']['section_type']}")
            print(f"   Type: {result['metadata']['chunk_type']}")
            
            # Show insurance terms found
            if 'insurance_terms' in result['metadata']:
                terms = {k: v for k, v in result['metadata']['insurance_terms'].items() if v > 0}
                if terms:
                    print(f"   Insurance Terms: {', '.join(terms.keys())}")
            
            # Show content preview
            content = result['content']
            if len(content) > 300:
                content = content[:300] + "..."
            print(f"   Content: {content}")
        
        # Record results
        query_record['results_count'] = len(results)
        query_record['top_score'] = results[0]['similarity_score'] if results else 0
        self.query_history.append(query_record)
    
    def _show_help(self) -> None:
        """Show help information"""
        print("\n=== Help ===")
        print("Commands:")
        print("  help     - Show this help")
        print("  stats    - Show system statistics")
        print("  history  - Show query history")
        print("  filter   - Show filtering options")
        print("  filter:section_type=coverage - Filter by section type")
        print("  filter:source_file=filename.pdf - Filter by source file")
        print("  quit     - Exit the system")
        print("\nExample queries:")
        print("  What are the coverage limits?")
        print("  What is excluded from coverage?")
        print("  How much is the premium?")
        print("  What are the claim procedures?")
        print("  What are the policy terms and conditions?")
    
    def _show_statistics(self) -> None:
        """Show system statistics"""
        stats = self.rag_system.get_statistics()
        print("\n=== System Statistics ===")
        print(f"Total Documents: {stats['total_documents']}")
        print(f"Total Chunks: {stats['total_chunks']}")
        print(f"Vector DB Size: {stats['vector_db_size']}")
        
        print("\nProcessed Files:")
        for filename, file_stats in stats['file_statistics'].items():
            print(f"  {filename}:")
            print(f"    Chunks: {file_stats['chunks']}")
            print(f"    Pages: {file_stats['pages']}")
            print(f"    Size: {file_stats['file_size_mb']:.2f} MB")
        
        print(f"\nQuery History: {len(self.query_history)} queries")
    
    def _show_query_history(self) -> None:
        """Show query history"""
        if not self.query_history:
            print("No query history available.")
            return
        
        print("\n=== Query History ===")
        for i, record in enumerate(self.query_history[-10:], 1):  # Show last 10
            print(f"{i}. Query: {record['query']}")
            print(f"   Results: {record['results_count']}")
            print(f"   Top Score: {record['top_score']:.3f}")
            print(f"   Time: {record['timestamp']}")
            if record['filter']:
                print(f"   Filter: {record['filter']}")
            print()
    
    def _show_filter_options(self) -> None:
        """Show available filtering options"""
        print("\n=== Filter Options ===")
        print("Available filters:")
        print("  section_type: coverage, exclusion, definition, condition, premium, claim, schedule, general")
        print("  chunk_type: text, table")
        print("  source_file: [filename.pdf]")
        print("  has_table_data: true/false")
        print("  has_legal_terms: true/false")
        print("\nUsage: filter:key=value")
        print("Example: filter:section_type=coverage")
    
    def _handle_filtered_query(self, filter_str: str) -> None:
        """Handle filtered query"""
        try:
            # Parse filter
            key, value = filter_str.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            # Convert boolean values
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            
            filter_metadata = {key: value}
            
            # Get query
            query = input("Enter your question: ").strip()
            if query:
                self._process_query(query, filter_metadata=filter_metadata)
                
        except ValueError:
            print("Invalid filter format. Use: filter:key=value")
        except Exception as e:
            print(f"Filter error: {e}")

class QueryEvaluator:
    """
    Evaluate query performance and accuracy
    """
    
    def __init__(self, rag_system: InsuranceRAGSystem):
        self.rag_system = rag_system
        self.evaluation_results = []
    
    def evaluate_queries(self, test_queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate a set of test queries"""
        print("Evaluating queries...")
        
        total_queries = len(test_queries)
        total_precision = 0
        total_recall = 0
        total_f1 = 0
        
        for i, test_case in enumerate(test_queries, 1):
            query = test_case['query']
            expected_sections = test_case.get('expected_sections', [])
            expected_keywords = test_case.get('expected_keywords', [])
            
            print(f"Evaluating query {i}/{total_queries}: {query}")
            
            # Get results
            results = self.rag_system.query(query, top_k=5)
            
            # Calculate metrics
            precision, recall, f1 = self._calculate_metrics(
                results, expected_sections, expected_keywords
            )
            
            total_precision += precision
            total_recall += recall
            total_f1 += f1
            
            # Record evaluation
            evaluation = {
                'query': query,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'results_count': len(results),
                'top_score': results[0]['similarity_score'] if results else 0
            }
            self.evaluation_results.append(evaluation)
        
        # Calculate averages
        avg_precision = total_precision / total_queries
        avg_recall = total_recall / total_queries
        avg_f1 = total_f1 / total_queries
        
        return {
            'total_queries': total_queries,
            'average_precision': avg_precision,
            'average_recall': avg_recall,
            'average_f1': avg_f1,
            'detailed_results': self.evaluation_results
        }
    
    def _calculate_metrics(self, results: List[Dict], expected_sections: List[str], 
                          expected_keywords: List[str]) -> tuple:
        """Calculate precision, recall, and F1 score"""
        if not results:
            return 0.0, 0.0, 0.0
        
        # Count relevant results
        relevant_count = 0
        for result in results:
            is_relevant = False
            
            # Check section type
            if expected_sections:
                if result['metadata']['section_type'] in expected_sections:
                    is_relevant = True
            
            # Check keywords
            if expected_keywords:
                content_lower = result['content'].lower()
                if any(keyword.lower() in content_lower for keyword in expected_keywords):
                    is_relevant = True
            
            if is_relevant:
                relevant_count += 1
        
        precision = relevant_count / len(results)
        recall = relevant_count / max(len(expected_sections) + len(expected_keywords), 1)
        
        # Calculate F1 score
        if precision + recall > 0:
            f1 = 2 * (precision * recall) / (precision + recall)
        else:
            f1 = 0.0
        
        return precision, recall, f1
    
    def generate_report(self, output_file: str = "evaluation_report.json") -> None:
        """Generate evaluation report"""
        if not self.evaluation_results:
            print("No evaluation results available.")
            return
        
        # Calculate summary statistics
        precisions = [r['precision'] for r in self.evaluation_results]
        recalls = [r['recall'] for r in self.evaluation_results]
        f1_scores = [r['f1_score'] for r in self.evaluation_results]
        
        report = {
            'summary': {
                'total_queries': len(self.evaluation_results),
                'average_precision': sum(precisions) / len(precisions),
                'average_recall': sum(recalls) / len(recalls),
                'average_f1': sum(f1_scores) / len(f1_scores),
                'min_precision': min(precisions),
                'max_precision': max(precisions),
                'min_recall': min(recalls),
                'max_recall': max(recalls),
                'min_f1': min(f1_scores),
                'max_f1': max(f1_scores)
            },
            'detailed_results': self.evaluation_results,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save report
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Evaluation report saved to {output_file}")
        
        # Display summary
        print("\n=== Evaluation Summary ===")
        print(f"Total Queries: {report['summary']['total_queries']}")
        print(f"Average Precision: {report['summary']['average_precision']:.3f}")
        print(f"Average Recall: {report['summary']['average_recall']:.3f}")
        print(f"Average F1 Score: {report['summary']['average_f1']:.3f}")

def main():
    """Main function for the query interface"""
    # Initialize RAG system
    rag_system = InsuranceRAGSystem("./Training_pdfs")
    
    # Check if documents are processed
    stats = rag_system.get_statistics()
    if stats['total_documents'] == 0:
        print("No documents processed. Processing PDFs...")
        rag_system.process_pdfs()
    
    # Initialize query interface
    interface = InsuranceQueryInterface(rag_system)
    
    # Start interactive session
    interface.interactive_query()

if __name__ == "__main__":
    main() 