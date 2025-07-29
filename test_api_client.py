#!/usr/bin/env python3
"""
Test client for the Insurance Policy RAG API
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
    """Test health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Check system status
            if data.get('status') == 'healthy':
                print("✓ API is healthy")
            else:
                print("⚠️ API is degraded")
                if not data.get('rag_system_ready'):
                    print("  - RAG system not ready")
                if not data.get('groq_ready'):
                    print("  - Groq API not ready")
                if not data.get('vector_db_ready'):
                    print("  - Vector database not ready")
            
            return True
        else:
            print(f"✗ Health check failed with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Connection failed. Make sure the API server is running.")
        print("  Start the server with: python api_backend.py")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_stats():
    """Test stats endpoint"""
    print("\nTesting stats endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/stats", headers=HEADERS, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if data.get('total_chunks', 0) > 0:
                print("✓ Vector database has data")
            else:
                print("⚠️ Vector database is empty")
            
            return True
        else:
            print(f"✗ Stats failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_query():
    """Test direct query endpoint"""
    print("\nTesting direct query...")
    try:
        params = {
            "question": "What is the grace period for premium payment?",
            "top_k": 3
        }
        response = requests.post(f"{BASE_URL}/api/v1/query", headers=HEADERS, params=params, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if data.get('total_results', 0) > 0:
                print("✓ Query returned results")
            else:
                print("⚠️ Query returned no results")
            
            return True
        else:
            print(f"✗ Query failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_run_submission():
    """Test the main run submission endpoint"""
    print("\nTesting run submission...")
    
    # Sample request based on the documentation
    payload = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
            "What is the waiting period for pre-existing diseases (PED) to be covered?",
            "Does this policy cover maternity expenses, and what are the conditions?"
        ]
    }
    
    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/v1/hackrx/run", headers=HEADERS, json=payload, timeout=60)
        end_time = time.time()
        
        print(f"Status: {response.status_code}")
        print(f"Response time: {end_time - start_time:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Run submission successful")
            print("Answers:")
            for i, answer in enumerate(result['answers'], 1):
                print(f"{i}. {answer}")
                print("-" * 50)
            return True
        else:
            print(f"✗ Run submission failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def check_environment():
    """Check environment configuration"""
    print("=== Environment Check ===")
    
    # Check .env file
    if os.path.exists(".env"):
        print("✓ .env file exists")
    else:
        print("✗ .env file not found")
        print("  Run: python setup_env.py")
        return False
    
    # Check Groq API key
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key and groq_key != "your-groq-api-key-here":
        print("✓ GROQ_API_KEY configured")
    else:
        print("⚠️ GROQ_API_KEY not configured")
        print("  Please set your Groq API key in .env file")
    
    # Check vector database
    if os.path.exists("vector_db"):
        print("✓ Vector database exists")
    else:
        print("✗ Vector database not found")
        return False
    
    return True

def main():
    """Run all tests"""
    print("Insurance Policy RAG API - Test Client")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("\nEnvironment check failed. Please fix the issues above.")
        return
    
    # Test health check
    health_ok = test_health_check()
    
    if not health_ok:
        print("\nHealth check failed. Make sure the API server is running.")
        print("Start the server with: python api_backend.py")
        return
    
    # Test stats
    stats_ok = test_stats()
    
    # Test direct query
    query_ok = test_query()
    
    # Test run submission
    run_ok = test_run_submission()
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Stats: {'✅ PASS' if stats_ok else '❌ FAIL'}")
    print(f"Direct Query: {'✅ PASS' if query_ok else '❌ FAIL'}")
    print(f"Run Submission: {'✅ PASS' if run_ok else '❌ FAIL'}")
    
    if all([health_ok, stats_ok, query_ok, run_ok]):
        print("\n🎉 All tests passed! The API is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the API server and configuration.")

if __name__ == "__main__":
    main() 