#!/usr/bin/env python3
"""
Production Test Suite for Qualcomm Linux RAG Q&A Service
Tests all endpoints and functionality for production readiness
"""

import os
import sys
import time
import requests
import json
from typing import Dict, Any, List
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8001"
API_KEY = os.getenv("API_KEY", "test_api_key")
TEST_TIMEOUT = 30

class ProductionTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.api_key = API_KEY
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:30} {status}")
        if details:
            print(f"  {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    def wait_for_server(self, max_retries: int = 30) -> bool:
        """Wait for server to be ready"""
        print("🔄 Waiting for server to be ready...")
        for i in range(max_retries):
            try:
                response = requests.get(f"{self.base_url}/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Server is ready!")
                    return True
            except:
                pass
            time.sleep(2)
            print(f"  Retry {i+1}/{max_retries}...")
        
        print("❌ Server failed to start within expected time")
        return False
    
    def test_health_endpoint(self) -> bool:
        """Test health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=TEST_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                assert data["status"] == "healthy"
                assert "timestamp" in data
                self.log_test("Health Endpoint", True)
                return True
            else:
                self.log_test("Health Endpoint", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Endpoint", False, str(e))
            return False
    
    def test_unauthorized_access(self) -> bool:
        """Test unauthorized access"""
        try:
            response = requests.get(f"{self.base_url}/info", timeout=TEST_TIMEOUT)
            if response.status_code == 401:
                self.log_test("Unauthorized Access", True)
                return True
            else:
                self.log_test("Unauthorized Access", False, f"Expected 401, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Unauthorized Access", False, str(e))
            return False
    
    def test_invalid_api_key(self) -> bool:
        """Test invalid API key"""
        try:
            headers = {"Authorization": "Bearer invalid_key"}
            response = requests.get(f"{self.base_url}/info", headers=headers, timeout=TEST_TIMEOUT)
            if response.status_code == 401:
                self.log_test("Invalid API Key", True)
                return True
            else:
                self.log_test("Invalid API Key", False, f"Expected 401, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Invalid API Key", False, str(e))
            return False
    
    def test_info_endpoint(self) -> bool:
        """Test info endpoint"""
        try:
            response = requests.get(f"{self.base_url}/info", headers=self.headers, timeout=TEST_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                required_fields = ["team_name", "model_info", "docs_count", "total_chunks", 
                                 "vector_db", "embedding_model", "chunk_size", "chunk_overlap", "timestamp"]
                for field in required_fields:
                    assert field in data
                self.log_test("Info Endpoint", True, f"Team: {data.get('team_name')}, Chunks: {data.get('total_chunks')}")
                return True
            else:
                self.log_test("Info Endpoint", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Info Endpoint", False, str(e))
            return False
    
    def test_stats_endpoint(self) -> bool:
        """Test stats endpoint"""
        try:
            response = requests.get(f"{self.base_url}/stats", headers=self.headers, timeout=TEST_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_queries", "avg_response_time_ms", "uptime_seconds"]
                for field in required_fields:
                    assert field in data
                self.log_test("Stats Endpoint", True, f"Queries: {data.get('total_queries')}, Uptime: {data.get('uptime_seconds')}s")
                return True
            else:
                self.log_test("Stats Endpoint", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Stats Endpoint", False, str(e))
            return False
    
    def test_context_endpoint(self) -> bool:
        """Test context endpoint"""
        try:
            payload = {
                "question": "What is Qualcomm Linux?",
                "max_results": 3
            }
            response = requests.post(f"{self.base_url}/context", headers=self.headers, json=payload, timeout=TEST_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                assert "question" in data
                assert "context_chunks" in data
                assert "total_chunks" in data
                assert "timestamp" in data
                self.log_test("Context Endpoint", True, f"Chunks returned: {data.get('total_chunks')}")
                return True
            else:
                self.log_test("Context Endpoint", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Context Endpoint", False, str(e))
            return False
    
    def test_query_endpoint(self) -> bool:
        """Test query endpoint"""
        try:
            payload = {
                "question": "What is Qualcomm Linux?",
                "max_results": 3,
                "include_sources": True
            }
            start_time = time.time()
            response = requests.post(f"{self.base_url}/query", headers=self.headers, json=payload, timeout=60)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["question", "answer", "sources", "total_tokens", 
                                 "vector_search_time", "llm_time", "total_time", "timestamp"]
                for field in required_fields:
                    assert field in data
                self.log_test("Query Endpoint", True, 
                            f"Response time: {response_time:.0f}ms, Tokens: {data.get('total_tokens')}")
                return True
            else:
                self.log_test("Query Endpoint", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Query Endpoint", False, str(e))
            return False
    
    def test_create_endpoint(self) -> bool:
        """Test create endpoint (will likely fail without PDFs)"""
        try:
            payload = {
                "folder_path": "/app/pdfs"
            }
            response = requests.post(f"{self.base_url}/create", headers=self.headers, json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Create Endpoint", True, f"Status: {data.get('status')}")
                return True
            elif response.status_code == 400:
                # Expected if no PDFs are available
                self.log_test("Create Endpoint", True, "No PDFs found (expected)")
                return True
            else:
                self.log_test("Create Endpoint", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Create Endpoint", False, str(e))
            return False
    
    def run_performance_test(self) -> bool:
        """Run performance test"""
        try:
            questions = [
                "What is Qualcomm Linux?",
                "How does the system work?",
                "What are the key features?",
                "Explain the architecture",
                "What are the requirements?"
            ]
            
            total_time = 0
            successful_queries = 0
            
            for question in questions:
                try:
                    payload = {
                        "question": question,
                        "max_results": 3,
                        "include_sources": True
                    }
                    start_time = time.time()
                    response = requests.post(f"{self.base_url}/query", headers=self.headers, json=payload, timeout=30)
                    query_time = (time.time() - start_time) * 1000
                    
                    if response.status_code == 200:
                        total_time += query_time
                        successful_queries += 1
                except:
                    pass
            
            if successful_queries > 0:
                avg_time = total_time / successful_queries
                self.log_test("Performance Test", True, 
                            f"Avg response time: {avg_time:.0f}ms ({successful_queries}/{len(questions)} queries)")
                return avg_time < 1000  # Should be under 1 second
            else:
                self.log_test("Performance Test", False, "No successful queries")
                return False
                
        except Exception as e:
            self.log_test("Performance Test", False, str(e))
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests"""
        print("🚀 Starting Production Test Suite")
        print("=" * 60)
        
        # Wait for server
        if not self.wait_for_server():
            return {"success": False, "error": "Server not ready"}
        
        # Run tests
        tests = [
            ("Health Endpoint", self.test_health_endpoint),
            ("Unauthorized Access", self.test_unauthorized_access),
            ("Invalid API Key", self.test_invalid_api_key),
            ("Info Endpoint", self.test_info_endpoint),
            ("Stats Endpoint", self.test_stats_endpoint),
            ("Context Endpoint", self.test_context_endpoint),
            ("Query Endpoint", self.test_query_endpoint),
            ("Create Endpoint", self.test_create_endpoint),
            ("Performance Test", self.run_performance_test),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running {test_name}...")
            if test_func():
                passed += 1
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{result['test']:30} {status}")
            if result["details"]:
                print(f"  {result['details']}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        success = passed == total
        if success:
            print("🎉 All tests passed! System is production-ready!")
        else:
            print("⚠️  Some tests failed. Check the logs above for details.")
        
        return {
            "success": success,
            "passed": passed,
            "total": total,
            "results": self.test_results
        }

def main():
    """Main test runner"""
    tester = ProductionTester()
    results = tester.run_all_tests()
    
    if results["success"]:
        print("\n🎯 Production readiness confirmed!")
        return True
    else:
        print("\n❌ Production readiness failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 