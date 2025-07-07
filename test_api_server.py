#!/usr/bin/env python3
"""
Test suite for the Qualcomm Linux RAG Q&A Service
"""

import os
import sys
import time
import requests
import json
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_health_endpoint(base_url: str) -> bool:
    """Test health endpoint"""
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "healthy"
            assert "timestamp" in data
            print("✓ Health endpoint test passed")
            return True
        else:
            print(f"✗ Health endpoint test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health endpoint test failed: {e}")
        return False

def test_info_endpoint(base_url: str, api_key: str) -> bool:
    """Test info endpoint"""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(f"{base_url}/info", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            required_fields = ["team_name", "model_info", "docs_count", "total_chunks", 
                             "vector_db", "embedding_model", "chunk_size", "chunk_overlap", "timestamp"]
            for field in required_fields:
                assert field in data
            print("✓ Info endpoint test passed")
            return True
        else:
            print(f"✗ Info endpoint test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Info endpoint test failed: {e}")
        return False

def test_stats_endpoint(base_url: str, api_key: str) -> bool:
    """Test stats endpoint"""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(f"{base_url}/stats", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            required_fields = ["total_queries", "avg_response_time_ms", "uptime_seconds"]
            for field in required_fields:
                assert field in data
            print("✓ Stats endpoint test passed")
            return True
        else:
            print(f"✗ Stats endpoint test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Stats endpoint test failed: {e}")
        return False

def test_context_endpoint(base_url: str, api_key: str) -> bool:
    """Test context endpoint"""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "question": "What is Qualcomm Linux?",
            "max_results": 3
        }
        response = requests.post(f"{base_url}/context", headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            assert "question" in data
            assert "context_chunks" in data
            assert "total_chunks" in data
            assert "timestamp" in data
            print("✓ Context endpoint test passed")
            return True
        else:
            print(f"✗ Context endpoint test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Context endpoint test failed: {e}")
        return False

def test_query_endpoint(base_url: str, api_key: str) -> bool:
    """Test query endpoint"""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "question": "What is Qualcomm Linux?",
            "max_results": 3,
            "include_sources": True
        }
        response = requests.post(f"{base_url}/query", headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json()
            required_fields = ["question", "answer", "sources", "total_tokens", 
                             "vector_search_time", "llm_time", "total_time", "timestamp"]
            for field in required_fields:
                assert field in data
            print("✓ Query endpoint test passed")
            return True
        else:
            print(f"✗ Query endpoint test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Query endpoint test failed: {e}")
        return False

def test_unauthorized_access(base_url: str) -> bool:
    """Test unauthorized access"""
    try:
        # Test without API key
        response = requests.get(f"{base_url}/info", timeout=10)
        if response.status_code == 401:
            print("✓ Unauthorized access test passed")
            return True
        else:
            print(f"✗ Unauthorized access test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Unauthorized access test failed: {e}")
        return False

def test_invalid_api_key(base_url: str) -> bool:
    """Test invalid API key"""
    try:
        headers = {"Authorization": "Bearer invalid_key"}
        response = requests.get(f"{base_url}/info", headers=headers, timeout=10)
        if response.status_code == 401:
            print("✓ Invalid API key test passed")
            return True
        else:
            print(f"✗ Invalid API key test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Invalid API key test failed: {e}")
        return False

def wait_for_server(base_url: str, max_retries: int = 30) -> bool:
    """Wait for server to be ready"""
    print("Waiting for server to be ready...")
    for i in range(max_retries):
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print("Server is ready!")
                return True
        except:
            pass
        time.sleep(2)
        print(f"Retry {i+1}/{max_retries}...")
    
    print("Server failed to start within expected time")
    return False

def main():
    """Run all tests"""
    print("Starting API server tests...")
    
    # Configuration
    base_url = "http://localhost:8000"
    api_key = os.getenv("API_KEY", "test_api_key")
    
    # Wait for server
    if not wait_for_server(base_url):
        print("❌ Server not ready, tests failed")
        sys.exit(1)
    
    # Run tests
    tests = [
        ("Health Endpoint", lambda: test_health_endpoint(base_url)),
        ("Unauthorized Access", lambda: test_unauthorized_access(base_url)),
        ("Invalid API Key", lambda: test_invalid_api_key(base_url)),
        ("Info Endpoint", lambda: test_info_endpoint(base_url, api_key)),
        ("Stats Endpoint", lambda: test_stats_endpoint(base_url, api_key)),
        ("Context Endpoint", lambda: test_context_endpoint(base_url, api_key)),
        ("Query Endpoint", lambda: test_query_endpoint(base_url, api_key)),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name} test...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 