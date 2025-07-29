import json
import logging
from typing import List, Dict, Any
from insurance_rag_system import InsuranceRAGSystem
from query_interface import QueryEvaluator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_queries() -> List[Dict[str, Any]]:
    """Create comprehensive test queries for insurance policy evaluation"""
    
    test_queries = [
        # Coverage-related queries
        {
            'query': 'What are the coverage limits?',
            'expected_sections': ['coverage', 'schedule'],
            'expected_keywords': ['limit', 'maximum', 'coverage', 'amount'],
            'category': 'coverage_limits'
        },
        {
            'query': 'What is covered under this policy?',
            'expected_sections': ['coverage'],
            'expected_keywords': ['cover', 'coverage', 'insured', 'benefits'],
            'category': 'coverage_scope'
        },
        {
            'query': 'What are the coverage exclusions?',
            'expected_sections': ['exclusion'],
            'expected_keywords': ['exclusion', 'excluded', 'not covered', 'except'],
            'category': 'exclusions'
        },
        
        # Premium and payment queries
        {
            'query': 'How much is the premium?',
            'expected_sections': ['premium', 'schedule'],
            'expected_keywords': ['premium', 'payment', 'cost', 'amount', '$'],
            'category': 'premium'
        },
        {
            'query': 'What are the payment terms?',
            'expected_sections': ['premium', 'condition'],
            'expected_keywords': ['payment', 'premium', 'due', 'installment'],
            'category': 'payment_terms'
        },
        {
            'query': 'What is the deductible amount?',
            'expected_sections': ['coverage', 'schedule'],
            'expected_keywords': ['deductible', 'excess', 'amount'],
            'category': 'deductible'
        },
        
        # Claims-related queries
        {
            'query': 'How do I file a claim?',
            'expected_sections': ['claim'],
            'expected_keywords': ['claim', 'file', 'procedure', 'notification'],
            'category': 'claim_procedure'
        },
        {
            'query': 'What documents are required for claims?',
            'expected_sections': ['claim'],
            'expected_keywords': ['document', 'proof', 'evidence', 'required'],
            'category': 'claim_documents'
        },
        {
            'query': 'What is the claims process?',
            'expected_sections': ['claim'],
            'expected_keywords': ['process', 'procedure', 'claim', 'settlement'],
            'category': 'claim_process'
        },
        
        # Policy terms and conditions
        {
            'query': 'What are the policy terms and conditions?',
            'expected_sections': ['condition', 'term'],
            'expected_keywords': ['term', 'condition', 'provision', 'clause'],
            'category': 'terms_conditions'
        },
        {
            'query': 'What is the policy period?',
            'expected_sections': ['schedule', 'condition'],
            'expected_keywords': ['period', 'duration', 'effective', 'expiry'],
            'category': 'policy_period'
        },
        {
            'query': 'What are the cancellation terms?',
            'expected_sections': ['condition'],
            'expected_keywords': ['cancel', 'termination', 'cancellation'],
            'category': 'cancellation'
        },
        
        # Definitions and legal terms
        {
            'query': 'What is the definition of insured?',
            'expected_sections': ['definition'],
            'expected_keywords': ['insured', 'definition', 'means', 'defined'],
            'category': 'definitions'
        },
        {
            'query': 'What does "pre-existing condition" mean?',
            'expected_sections': ['definition', 'exclusion'],
            'expected_keywords': ['pre-existing', 'condition', 'definition'],
            'category': 'definitions'
        },
        {
            'query': 'What are the policy definitions?',
            'expected_sections': ['definition'],
            'expected_keywords': ['definition', 'defined', 'means'],
            'category': 'definitions'
        },
        
        # Specific coverage types
        {
            'query': 'What is covered for hospitalization?',
            'expected_sections': ['coverage'],
            'expected_keywords': ['hospitalization', 'hospital', 'inpatient'],
            'category': 'specific_coverage'
        },
        {
            'query': 'What is covered for outpatient treatment?',
            'expected_sections': ['coverage'],
            'expected_keywords': ['outpatient', 'treatment', 'consultation'],
            'category': 'specific_coverage'
        },
        {
            'query': 'What is covered for prescription drugs?',
            'expected_sections': ['coverage'],
            'expected_keywords': ['prescription', 'drug', 'medicine', 'medication'],
            'category': 'specific_coverage'
        },
        
        # Network and provider queries
        {
            'query': 'What is the network coverage?',
            'expected_sections': ['coverage', 'condition'],
            'expected_keywords': ['network', 'provider', 'hospital', 'doctor'],
            'category': 'network'
        },
        {
            'query': 'Can I use any doctor?',
            'expected_sections': ['coverage', 'condition'],
            'expected_keywords': ['doctor', 'provider', 'network', 'any'],
            'category': 'network'
        },
        
        # Emergency and urgent care
        {
            'query': 'What is covered for emergency treatment?',
            'expected_sections': ['coverage'],
            'expected_keywords': ['emergency', 'urgent', 'accident'],
            'category': 'emergency'
        },
        {
            'query': 'What should I do in an emergency?',
            'expected_sections': ['claim', 'condition'],
            'expected_keywords': ['emergency', 'urgent', 'immediate'],
            'category': 'emergency'
        },
        
        # Renewal and changes
        {
            'query': 'How do I renew the policy?',
            'expected_sections': ['condition'],
            'expected_keywords': ['renew', 'renewal', 'continue'],
            'category': 'renewal'
        },
        {
            'query': 'Can I change my coverage?',
            'expected_sections': ['condition'],
            'expected_keywords': ['change', 'modify', 'endorsement', 'rider'],
            'category': 'changes'
        },
        
        # Complex queries
        {
            'query': 'What is the maximum coverage for critical illness with pre-existing conditions?',
            'expected_sections': ['coverage', 'exclusion', 'schedule'],
            'expected_keywords': ['critical illness', 'pre-existing', 'maximum', 'limit'],
            'category': 'complex_coverage'
        },
        {
            'query': 'What are the waiting periods and exclusions for maternity coverage?',
            'expected_sections': ['coverage', 'exclusion', 'condition'],
            'expected_keywords': ['waiting period', 'maternity', 'exclusion'],
            'category': 'complex_coverage'
        }
    ]
    
    return test_queries

def run_comprehensive_evaluation():
    """Run comprehensive evaluation of the RAG system"""
    
    print("=== Insurance Policy RAG System - Comprehensive Evaluation ===")
    
    # Initialize RAG system
    rag_system = InsuranceRAGSystem("./Training_pdfs")
    
    # Check if documents are processed
    stats = rag_system.get_statistics()
    if stats['total_documents'] == 0:
        print("No documents processed. Processing PDFs...")
        rag_system.process_pdfs()
    
    # Initialize evaluator
    evaluator = QueryEvaluator(rag_system)
    
    # Create test queries
    test_queries = create_test_queries()
    
    print(f"\nRunning evaluation on {len(test_queries)} test queries...")
    
    # Run evaluation
    results = evaluator.evaluate_queries(test_queries)
    
    # Generate detailed report
    evaluator.generate_report("comprehensive_evaluation_report.json")
    
    # Additional analysis by category
    analyze_by_category(test_queries, evaluator.evaluation_results)
    
    return results

def analyze_by_category(test_queries: List[Dict], evaluation_results: List[Dict]):
    """Analyze performance by query category"""
    
    # Group results by category
    category_results = {}
    for i, result in enumerate(evaluation_results):
        category = test_queries[i]['category']
        if category not in category_results:
            category_results[category] = []
        category_results[category].append(result)
    
    # Calculate category-wise metrics
    category_metrics = {}
    for category, results in category_results.items():
        if results:
            avg_precision = sum(r['precision'] for r in results) / len(results)
            avg_recall = sum(r['recall'] for r in results) / len(results)
            avg_f1 = sum(r['f1_score'] for r in results) / len(results)
            
            category_metrics[category] = {
                'count': len(results),
                'avg_precision': avg_precision,
                'avg_recall': avg_recall,
                'avg_f1': avg_f1
            }
    
    # Display category analysis
    print("\n=== Performance by Category ===")
    for category, metrics in category_metrics.items():
        print(f"\n{category.upper()}:")
        print(f"  Queries: {metrics['count']}")
        print(f"  Avg Precision: {metrics['avg_precision']:.3f}")
        print(f"  Avg Recall: {metrics['avg_recall']:.3f}")
        print(f"  Avg F1: {metrics['avg_f1']:.3f}")
    
    # Save category analysis
    with open("category_analysis.json", 'w') as f:
        json.dump(category_metrics, f, indent=2)
    
    print(f"\nCategory analysis saved to category_analysis.json")

def run_specific_tests():
    """Run specific targeted tests"""
    
    print("\n=== Running Specific Tests ===")
    
    # Initialize RAG system
    rag_system = InsuranceRAGSystem("./Training_pdfs")
    
    # Specific test cases
    specific_tests = [
        {
            'name': 'Coverage Limit Test',
            'query': 'What is the maximum coverage amount?',
            'expected_keywords': ['maximum', 'limit', 'coverage', 'amount']
        },
        {
            'name': 'Exclusion Test',
            'query': 'What is not covered?',
            'expected_keywords': ['exclusion', 'excluded', 'not covered']
        },
        {
            'name': 'Premium Test',
            'query': 'How much do I need to pay?',
            'expected_keywords': ['premium', 'payment', 'cost', '$']
        },
        {
            'name': 'Claim Procedure Test',
            'query': 'How to make a claim?',
            'expected_keywords': ['claim', 'procedure', 'file', 'submit']
        }
    ]
    
    for test in specific_tests:
        print(f"\n--- {test['name']} ---")
        print(f"Query: {test['query']}")
        
        results = rag_system.query(test['query'], top_k=3)
        
        if results:
            print("Top Results:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. Score: {result['similarity_score']:.3f}")
                print(f"     Section: {result['metadata']['section_type']}")
                print(f"     Content: {result['content'][:150]}...")
                
                # Check for expected keywords
                content_lower = result['content'].lower()
                found_keywords = [kw for kw in test['expected_keywords'] if kw.lower() in content_lower]
                if found_keywords:
                    print(f"     Keywords found: {', '.join(found_keywords)}")
        else:
            print("No results found.")

def main():
    """Main evaluation function"""
    
    print("Insurance Policy RAG System - Evaluation Suite")
    print("=" * 50)
    
    # Run comprehensive evaluation
    results = run_comprehensive_evaluation()
    
    # Run specific tests
    run_specific_tests()
    
    print("\n=== Evaluation Complete ===")
    print(f"Overall Performance:")
    print(f"  Average Precision: {results['average_precision']:.3f}")
    print(f"  Average Recall: {results['average_recall']:.3f}")
    print(f"  Average F1 Score: {results['average_f1']:.3f}")
    
    # Performance assessment
    if results['average_f1'] >= 0.8:
        print("  Assessment: EXCELLENT - High accuracy and precision")
    elif results['average_f1'] >= 0.6:
        print("  Assessment: GOOD - Reasonable accuracy and precision")
    elif results['average_f1'] >= 0.4:
        print("  Assessment: FAIR - Moderate accuracy, room for improvement")
    else:
        print("  Assessment: NEEDS IMPROVEMENT - Low accuracy, requires optimization")

if __name__ == "__main__":
    main() 