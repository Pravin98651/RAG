#!/usr/bin/env python3
"""
Quick API test to verify endpoints are working
"""

import requests
import json
import time

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health Check: PASSED")
            print(f"   Status: {data['status']}")
            print(f"   RAG System: {data['rag_system_ready']}")
            print(f"   Groq API: {data['groq_ready']}")
            print(f"   Vector DB: {data['vector_db_ready']}")
            return True
        else:
            print(f"❌ Health Check: FAILED ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Health Check: ERROR - {e}")
        return False

def test_llm_integration():
    """Test LLM integration"""
    headers = {
        "Authorization": "Bearer c94dfd1ae12b50eb392cd6d1ef5f4578c561f54bacf6cd6849236cbfc2e8b673",
        "Content-Type": "application/json"
    }
    
    payload = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment?"
        ]
    }
    
    try:
        print("\n🔄 Testing LLM Integration...")
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:8000/api/v1/hackrx/run",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            print("✅ LLM Integration: PASSED")
            print(f"   Response Time: {response_time:.2f} seconds")
            print(f"   Questions Processed: {len(data['answers'])}")
            print(f"   Answer: {data['answers'][0]}")
            return True
        else:
            print(f"❌ LLM Integration: FAILED ({response.status_code})")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ LLM Integration: ERROR - {e}")
        return False

def test_stats():
    """Test stats endpoint"""
    headers = {
        "Authorization": "Bearer c94dfd1ae12b50eb392cd6d1ef5f4578c561f54bacf6cd6849236cbfc2e8b673"
    }
    
    try:
        response = requests.get("http://localhost:8000/api/v1/stats", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Stats Endpoint: PASSED")
            print(f"   Total Chunks: {data['total_chunks']}")
            print(f"   Total Documents: {data['total_documents']}")
            print(f"   Files: {data['processed_files']}")
            return True
        else:
            print(f"❌ Stats Endpoint: FAILED ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Stats Endpoint: ERROR - {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Quick API Test")
    print("=" * 40)
    
    # Test health
    health_ok = test_health()
    
    if health_ok:
        # Test stats
        stats_ok = test_stats()
        
        # Test LLM integration
        llm_ok = test_llm_integration()
        
        # Summary
        print("\n" + "=" * 40)
        print("📊 TEST RESULTS")
        print("=" * 40)
        print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
        print(f"Stats: {'✅ PASS' if stats_ok else '❌ FAIL'}")
        print(f"LLM Integration: {'✅ PASS' if llm_ok else '❌ FAIL'}")
        
        if all([health_ok, stats_ok, llm_ok]):
            print("\n🎉 ALL TESTS PASSED!")
            print("\nYour RAG API with LLM integration is working perfectly!")
            print("\nYou can now:")
            print("• Use the API in your applications")
            print("• Access docs: http://localhost:8000/docs")
            print("• Send questions to get AI answers")
        else:
            print(f"\n⚠️ Some tests failed. Check the server logs.")
    else:
        print("\n❌ Health check failed. Make sure the server is running.")

if __name__ == "__main__":
    main() 