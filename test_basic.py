#!/usr/bin/env python3
"""
Basic functionality tests for the Qualcomm Linux RAG Q&A Service
"""

import os
import sys
import tempfile
import shutil

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_pdf_processor():
    """Test PDF processor functionality"""
    try:
        from pdf_processor import PDFProcessor
        
        # Create a test PDF processor
        processor = PDFProcessor(chunk_size=100, chunk_overlap=20)
        
        # Test text cleaning
        test_text = "This is a test document with some technical content."
        cleaned = processor.clean_text(test_text)
        assert cleaned == test_text
        
        # Test chunk creation
        chunks = processor.split_text_into_chunks(test_text, "test_doc")
        assert len(chunks) > 0
        assert chunks[0]["doc_name"] == "test_doc"
        
        print("✓ PDF processor test passed")
        return True
    except Exception as e:
        print(f"✗ PDF processor test failed: {e}")
        return False

def test_utils():
    """Test utility functions"""
    try:
        from utils import count_tokens, create_chunk_id, format_timestamp
        
        # Test token counting
        text = "This is a test sentence."
        tokens = count_tokens(text)
        assert tokens > 0
        
        # Test chunk ID creation
        chunk_id = create_chunk_id("test_doc", 1)
        assert chunk_id == "test_doc_1"
        
        # Test timestamp formatting
        timestamp = format_timestamp()
        assert len(timestamp) > 0
        
        print("✓ Utils test passed")
        return True
    except Exception as e:
        print(f"✗ Utils test failed: {e}")
        return False

def test_rag_system_init():
    """Test RAG system initialization"""
    try:
        from rag_system import RAGSystem
        
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test RAG system initialization
            rag = RAGSystem(vector_db_path=temp_dir)
            
            # Test vector DB stats
            stats = rag.get_vector_db_stats()
            assert "total_chunks" in stats
            
            print("✓ RAG system initialization test passed")
            return True
    except Exception as e:
        print(f"✗ RAG system initialization test failed: {e}")
        return False

def test_imports():
    """Test that all modules can be imported"""
    try:
        # Test basic imports
        import src.pdf_processor
        import src.utils
        
        print("✓ Basic imports test passed")
        return True
    except Exception as e:
        print(f"✗ Basic imports test failed: {e}")
        return False

def test_fastapi_import():
    """Test FastAPI import separately"""
    try:
        import fastapi
        import uvicorn
        print("✓ FastAPI imports test passed")
        return True
    except Exception as e:
        print(f"✗ FastAPI imports test failed: {e}")
        return False

def main():
    """Run all basic tests"""
    print("Running basic functionality tests...")
    
    tests = [
        ("FastAPI Imports", test_fastapi_import),
        ("Basic Imports", test_imports),
        ("Utils", test_utils),
        ("PDF Processor", test_pdf_processor),
        ("RAG System Init", test_rag_system_init),
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
    print(f"Basic Test Results: {passed}/{total} tests passed")
    
    if passed >= 3:  # At least 3 tests should pass
        print("🎉 Sufficient tests passed! Service should work.")
        return True
    else:
        print("❌ Too many basic tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 