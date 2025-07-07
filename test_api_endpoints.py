#!/usr/bin/env python3
"""
Test script for Multimodal RAG API Endpoints
Tests all the required endpoints with sample data
"""

import requests
import json
import time
from typing import Dict, Any

# API Configuration
BASE_URL = "http://localhost:8000"
API_ENDPOINTS = {
    "health": "/health",
    "info": "/info", 
    "stats": "/stats",
    "create": "/create",
    "context": "/context",
    "query": "/query",
    "collections": "/collections"
}

def test_health_endpoint() -> Dict[str, Any]:
    """Test GET /health endpoint"""
    print("🔍 Testing /health endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Health check passed: {data}")
        return {"success": True, "data": data}
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return {"success": False, "error": str(e)}

def test_info_endpoint() -> Dict[str, Any]:
    """Test GET /info endpoint"""
    print("\n🔍 Testing /info endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/info")
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Info retrieved successfully:")
        print(f"   - Team: {data.get('team_name')}")
        print(f"   - Model: {data.get('model_info')}")
        print(f"   - Documents: {data.get('docs_count')}")
        print(f"   - Chunks: {data.get('total_chunks')}")
        print(f"   - Vector DB: {data.get('vector_db')}")
        print(f"   - Embedding Model: {data.get('embedding_model')}")
        print(f"   - Chunk Size: {data.get('chunk_size')}")
        print(f"   - Chunk Overlap: {data.get('chunk_overlap')}")
        
        return {"success": True, "data": data}
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Info endpoint failed: {e}")
        return {"success": False, "error": str(e)}

def test_stats_endpoint() -> Dict[str, Any]:
    """Test GET /stats endpoint"""
    print("\n🔍 Testing /stats endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/stats")
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Stats retrieved successfully:")
        print(f"   - Total Queries: {data.get('total_queries')}")
        print(f"   - Avg Response Time: {data.get('avg_response_time_ms'):.2f}ms")
        print(f"   - Uptime: {data.get('uptime_seconds')} seconds")
        
        return {"success": True, "data": data}
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Stats endpoint failed: {e}")
        return {"success": False, "error": str(e)}

def test_create_endpoint(folder_path: str = "/app/pdfs") -> Dict[str, Any]:
    """Test POST /create endpoint"""
    print(f"\n🔍 Testing /create endpoint with folder: {folder_path}")
    
    try:
        payload = {
            "folder_path": folder_path
        }
        
        response = requests.post(
            f"{BASE_URL}/create",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Vector database created successfully:")
            print(f"   - Success: {data.get('success')}")
            print(f"   - Message: {data.get('message')}")
            print(f"   - Collection: {data.get('collection_name')}")
            print(f"   - Documents Processed: {data.get('documents_processed')}")
            print(f"   - Pages Processed: {data.get('pages_processed')}")
            
            if data.get('processing_stats'):
                stats = data['processing_stats']
                print(f"   - Processing Stats:")
                print(f"     * Total Pages: {stats.get('total_pages')}")
                print(f"     * Total Chunks: {stats.get('total_chunks')}")
                print(f"     * Pages with Text: {stats.get('pages_with_text')}")
                print(f"     * Pages with Images: {stats.get('pages_with_images')}")
                print(f"     * Total Images: {stats.get('total_images')}")
            
            return {"success": True, "data": data}
        else:
            print(f"❌ Create endpoint failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return {"success": False, "error": response.text}
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Create endpoint failed: {e}")
        return {"success": False, "error": str(e)}

def test_context_endpoint(question: str = "What is the main topic?") -> Dict[str, Any]:
    """Test POST /context endpoint"""
    print(f"\n🔍 Testing /context endpoint with question: '{question}'")
    
    try:
        payload = {
            "question": question
        }
        
        response = requests.post(
            f"{BASE_URL}/context",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Context retrieved successfully:")
            print(f"   - Question: {data.get('question')}")
            print(f"   - Total Results: {data.get('total_results')}")
            print(f"   - Sources: {len(data.get('sources', []))}")
            
            # Show first few context snippets
            context = data.get('context', [])
            for i, snippet in enumerate(context[:3]):
                print(f"   - Context {i+1}: {snippet[:100]}...")
            
            return {"success": True, "data": data}
        else:
            print(f"❌ Context endpoint failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return {"success": False, "error": response.text}
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Context endpoint failed: {e}")
        return {"success": False, "error": str(e)}

def test_query_endpoint(question: str = "What is the main topic?", max_results: int = 5) -> Dict[str, Any]:
    """Test POST /query endpoint"""
    print(f"\n🔍 Testing /query endpoint with question: '{question}'")
    
    try:
        payload = {
            "question": question,
            "max_results": max_results,
            "include_sources": True
        }
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/query",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        request_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Query processed successfully:")
            print(f"   - Question: {data.get('question')}")
            print(f"   - Answer: {data.get('answer')[:200]}...")
            print(f"   - Response Time: {data.get('response_time_ms'):.2f}ms")
            print(f"   - Context Documents: {data.get('context_documents')}")
            print(f"   - Sources: {len(data.get('sources', []))}")
            print(f"   - Request Time: {request_time:.2f}ms")
            
            # Show processing stats
            stats = data.get('processing_stats', {})
            if stats:
                print(f"   - Processing Stats:")
                print(f"     * Total Chunks: {stats.get('total_chunks_processed')}")
                print(f"     * Avg Similarity: {stats.get('avg_similarity_score', 0):.3f}")
                print(f"     * Has Images: {stats.get('has_images', False)}")
            
            return {"success": True, "data": data}
        else:
            print(f"❌ Query endpoint failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return {"success": False, "error": response.text}
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Query endpoint failed: {e}")
        return {"success": False, "error": str(e)}

def test_collections_endpoint() -> Dict[str, Any]:
    """Test GET /collections endpoint"""
    print("\n🔍 Testing /collections endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/collections")
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Collections retrieved successfully:")
        print(f"   - Total Collections: {data.get('total_collections')}")
        print(f"   - Collections: {data.get('collections')}")
        
        return {"success": True, "data": data}
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Collections endpoint failed: {e}")
        return {"success": False, "error": str(e)}

def test_collection_info_endpoint(collection_name: str = "default") -> Dict[str, Any]:
    """Test GET /collections/{collection_name} endpoint"""
    print(f"\n🔍 Testing /collections/{collection_name} endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/collections/{collection_name}")
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Collection info retrieved successfully:")
        print(f"   - Collection: {data.get('name')}")
        print(f"   - Exists: {data.get('exists')}")
        print(f"   - Document Count: {data.get('document_count')}")
        
        return {"success": True, "data": data}
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Collection info endpoint failed: {e}")
        return {"success": False, "error": str(e)}

def run_comprehensive_test():
    """Run comprehensive test of all endpoints"""
    print("🚀 Starting Comprehensive API Test Suite")
    print("=" * 60)
    
    results = {}
    
    # Test basic endpoints
    results["health"] = test_health_endpoint()
    results["info"] = test_info_endpoint()
    results["stats"] = test_stats_endpoint()
    results["collections"] = test_collections_endpoint()
    
    # Test collection info
    results["collection_info"] = test_collection_info_endpoint()
    
    # Test create endpoint (this might fail if no PDFs are available)
    results["create"] = test_create_endpoint()
    
    # Test context and query endpoints
    results["context"] = test_context_endpoint()
    results["query"] = test_query_endpoint()
    
    # Test with different questions
    test_questions = [
        "What are the key features?",
        "Are there any images or diagrams?",
        "What is the conclusion?"
    ]
    
    for i, question in enumerate(test_questions):
        results[f"query_{i+1}"] = test_query_endpoint(question)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    successful_tests = 0
    total_tests = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result.get("success") else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result.get("success"):
            successful_tests += 1
    
    print(f"\nOverall: {successful_tests}/{total_tests} tests passed")
    
    if successful_tests == total_tests:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
    
    return results

def test_with_sample_pdfs():
    """Test with sample PDFs if available"""
    print("\n🔍 Testing with sample PDFs...")
    
    # Check if sample PDFs exist
    sample_pdfs = [
        "sample.pdf",
        "test.pdf", 
        "document.pdf"
    ]
    
    for pdf in sample_pdfs:
        try:
            with open(pdf, 'rb') as f:
                print(f"Found sample PDF: {pdf}")
        except FileNotFoundError:
            print(f"Sample PDF not found: {pdf}")
    
    print("To test with your own PDFs:")
    print("1. Place PDF files in the ./pdfs/ directory")
    print("2. Run: python test_api_endpoints.py")
    print("3. The system will automatically process them")

if __name__ == "__main__":
    print("🧪 Multimodal RAG API Test Suite")
    print("Testing all required endpoints...")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and accessible")
        else:
            print("❌ Server responded but health check failed")
            exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on localhost:8000")
        print("Start the server with: docker-compose up")
        exit(1)
    
    # Run tests
    results = run_comprehensive_test()
    
    # Test with sample PDFs
    test_with_sample_pdfs()
    
    print("\n🏁 Test suite completed!") 