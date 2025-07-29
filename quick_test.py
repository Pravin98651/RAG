#!/usr/bin/env python3
"""
Quick test for the Insurance Policy RAG API
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
    try:
        headers = {
            "Authorization": "Bearer c94dfd1ae12b50eb392cd6d1ef5f4578c561f54bacf6cd6849236cbfc2e8b673"
        }
        response = requests.get("http://localhost:8000/api/v1/stats", headers=headers, timeout=10)
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

def main():
    """Main test function"""
    print("Quick API Test")
    print("=" * 30)
    
    # Wait a moment for server to start
    print("Waiting for server...")
    time.sleep(3)
    
    # Test health
    health_ok = test_health()
    
    if health_ok:
        # Test stats
        stats_ok = test_stats()
        
        if stats_ok:
            print("\n🎉 API is working correctly!")
            print("\nYou can now:")
            print("1. Access API docs: http://localhost:8000/docs")
            print("2. Test the main endpoint with your questions")
            print("3. Use the API in your applications")
        else:
            print("\n⚠️ Stats endpoint failed")
    else:
        print("\n❌ Health check failed")
        print("Make sure the server is running: python api_backend.py")

if __name__ == "__main__":
    main() 