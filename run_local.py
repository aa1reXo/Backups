#!/usr/bin/env python3
"""
Local runner for Qualcomm Linux RAG Q&A Service
Runs the service directly without Docker containers
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.10+"""
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ is required. Current version:", sys.version)
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def setup_directories():
    """Create necessary directories"""
    print("📁 Setting up directories...")
    directories = ["data", "logs", "pdfs", "local/mnt/workspace/sparq25"]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def setup_environment():
    """Set up environment variables"""
    print("🔧 Setting up environment...")
    
    # Set API keys
    os.environ["API_KEY"] = "AIzaSyAVBDGK6lP9SjFuAG0c3VxJ3Jly25LUBy0"
    os.environ["GOOGLE_API_KEY"] = "AIzaSyAVBDGK6lP9SjFuAG0c3VxJ3Jly25LUBy0"
    
    # Set ChromaDB environment
    os.environ["CHROMA_DB_IMPL"] = "duckdb+parquet"
    os.environ["PERSIST_DIRECTORY"] = "./data"
    
    print("✅ Environment variables set")

def install_system_dependencies():
    """Install system dependencies (for OCR)"""
    print("🔧 Installing system dependencies...")
    
    # Check if we're on macOS
    if sys.platform == "darwin":
        try:
            # Check if tesseract is installed
            result = subprocess.run(["tesseract", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Tesseract OCR already installed")
                return True
            else:
                print("⚠️ Tesseract OCR not found. Install with: brew install tesseract")
                print("   OCR functionality will be limited")
                return True
        except FileNotFoundError:
            print("⚠️ Tesseract OCR not found. Install with: brew install tesseract")
            print("   OCR functionality will be limited")
            return True
    
    # For Linux, provide instructions
    elif sys.platform.startswith("linux"):
        print("⚠️ For Linux, install Tesseract with: sudo apt-get install tesseract-ocr")
        print("   OCR functionality will be limited")
        return True
    
    # For Windows, provide instructions
    elif sys.platform.startswith("win"):
        print("⚠️ For Windows, install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("   OCR functionality will be limited")
        return True
    
    return True

def run_tests():
    """Run basic tests"""
    print("🧪 Running basic tests...")
    try:
        # Add src to Python path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        # Import and test basic functionality
        from src.api_server import app
        from src.rag_system import RAGSystem
        from src.pdf_processor import PDFProcessor
        
        print("✅ Basic imports successful")
        return True
    except Exception as e:
        print(f"❌ Basic tests failed: {e}")
        return False

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting FastAPI server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📍 Web UI will be available at: http://localhost:8081")
    print("🔑 API Key: AIzaSyAVBDGK6lP9SjFuAG0c3VxJ3Jly25LUBy0")
    print("")
    print("📋 Available endpoints:")
    print("   GET  /health - Health check")
    print("   GET  /info - System information")
    print("   GET  /stats - Performance statistics")
    print("   GET  /performance - Performance recommendations")
    print("   POST /create - Create vector database")
    print("   POST /context - Get context for question")
    print("   POST /query - Ask questions")
    print("")
    print("💡 To stop the server, press Ctrl+C")
    print("")
    
    try:
        # Start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "src.api_server:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")

def main():
    """Main function"""
    print("🔍 Qualcomm Linux RAG Q&A Service - Local Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Setup directories
    setup_directories()
    
    # Setup environment
    setup_environment()
    
    # Install system dependencies
    install_system_dependencies()
    
    # Run tests
    if not run_tests():
        print("⚠️ Tests failed, but continuing...")
    
    print("")
    print("✅ Setup complete!")
    print("")
    
    # Start server
    start_server()

if __name__ == "__main__":
    main() 