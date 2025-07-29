#!/usr/bin/env python3
"""
Test script to verify LLM and API functionality
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
BASE_URL = "http://localhost:8000"
API_TOKEN = os.getenv("API_TOKEN", "c94dfd1ae12b50eb392cd6d1ef5f4578c561f54bacf6cd6849236cbfc2e8b673")
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def test_health_check():
    """Test health endpoint"""
    print("1. Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✓ Health check passed")
            print(f"  Status: {data['status']}")
            print(f"  RAG System: {data['rag_system_ready']}")
            print(f"  Groq API: {data['groq_ready']}")
            print(f"  Vector DB: {data['vector_db_ready']}")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False

def test_stats():
    """Test stats endpoint"""
    print("\n2. Testing Stats Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/stats", headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✓ Stats endpoint passed")
            print(f"  Total chunks: {data['total_chunks']}")
            print(f"  Total documents: {data['total_documents']}")
            print(f"  Files: {data['processed_files']}")
            return True
        else:
            print(f"✗ Stats failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Stats error: {e}")
        return False

def test_direct_query():
    """Test direct RAG query (without LLM)"""
    print("\n3. Testing Direct RAG Query...")
    try:
        params = {
            "question": "What is the grace period for premium payment?",
            "top_k": 3
        }
        response = requests.post(f"{BASE_URL}/api/v1/query", headers=HEADERS, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print("✓ Direct query passed")
            print(f"  Question: {data['question']}")
            print(f"  Results: {data['total_results']}")
            
            if data['results']:
                print("  Top result:")
                print(f"    Source: {data['results'][0]['metadata']['source_file']}")
                print(f"    Score: {data['results'][0]['similarity_score']:.3f}")
                print(f"    Content: {data['results'][0]['content'][:200]}...")
            
            return True
        else:
            print(f"✗ Direct query failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Direct query error: {e}")
        return False

def test_llm_integration():
    """Test LLM integration with RAG"""
    print("\n4. Testing LLM Integration...")
    
    # Sample request based on your API documentation
    payload = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
            "What is the waiting period for pre-existing diseases (PED) to be covered?",
            "Does this policy cover maternity expenses, and what are the conditions?"
        ]
    }
    
    try:
        print("  Sending request to /api/v1/hackrx/run...")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/api/v1/hackrx/run", 
            headers=HEADERS, 
            json=payload, 
            timeout=60
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"  Response time: {response_time:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ LLM integration passed")
            print(f"  Questions processed: {len(data['answers'])}")
            
            for i, answer in enumerate(data['answers'], 1):
                print(f"\n  Answer {i}:")
                print(f"    Question: {payload['questions'][i-1]}")
                print(f"    Answer: {answer}")
                print("-" * 50)
            
            return True
        else:
            print(f"✗ LLM integration failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ LLM integration error: {e}")
        return False

def test_simple_question():
    """Test a simple question to verify LLM is working"""
    print("\n5. Testing Simple Question...")
    
    payload = {
        "documents": "https://example.com/policy.pdf",
        "questions": [
            "What is the grace period for premium payment?"
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/hackrx/run", 
            headers=HEADERS, 
            json=payload, 
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Simple question test passed")
            print(f"  Answer: {data['answers'][0]}")
            return True
        else:
            print(f"✗ Simple question failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Simple question error: {e}")
        return False

def main():
    """Main test function"""
    print("Insurance Policy RAG API - LLM Integration Test")
    print("=" * 60)
    
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(5)
    
    # Run all tests
    tests = [
        ("Health Check", test_health_check),
        ("Stats", test_stats),
        ("Direct RAG Query", test_direct_query),
        ("LLM Integration", test_llm_integration),
        ("Simple Question", test_simple_question)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nYour RAG API with LLM integration is working perfectly!")
        print("\nYou can now:")
        print("1. Use the API in your applications")
        print("2. Access interactive docs: http://localhost:8000/docs")
        print("3. Send questions to get AI-generated answers")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        print("Check the server logs for more details")

if __name__ == "__main__":
    main() 