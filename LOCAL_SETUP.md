# Local Setup Guide - Without Docker

This guide will help you run the Qualcomm Linux RAG Q&A Service directly on your system without Docker containers.

## Prerequisites

### 1. Python 3.10+
Make sure you have Python 3.10 or higher installed:

```bash
python --version
# or
python3 --version
```

### 2. System Dependencies

#### macOS
```bash
# Install Tesseract OCR (optional, for image processing)
brew install tesseract

# Install other dependencies
brew install python3
```

#### Linux (Ubuntu/Debian)
```bash
# Install Tesseract OCR (optional, for image processing)
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-eng

# Install Python dependencies
sudo apt-get install python3 python3-pip python3-venv
```

#### Windows
1. Download and install Python 3.10+ from [python.org](https://python.org)
2. Download Tesseract from [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)

## Quick Start

### Option 1: Automated Setup (Recommended)

1. **Run the automated setup script:**
```bash
python run_local.py
```

This script will:
- ✅ Check Python version
- ✅ Install all requirements
- ✅ Create necessary directories
- ✅ Set up environment variables
- ✅ Run basic tests
- ✅ Start the FastAPI server

### Option 2: Manual Setup

1. **Install Python requirements:**
```bash
pip install -r requirements.txt
```

2. **Create directories:**
```bash
mkdir -p data logs pdfs local/mnt/workspace/sparq25
```

3. **Set environment variables:**
```bash
export API_KEY="AIzaSyAVBDGK6lP9SjFuAG0c3VxJ3Jly25LUBy0"
export GOOGLE_API_KEY="AIzaSyAVBDGK6lP9SjFuAG0c3VxJ3Jly25LUBy0"
export CHROMA_DB_IMPL="duckdb+parquet"
export PERSIST_DIRECTORY="./data"
```

4. **Start the FastAPI server:**
```bash
python -m uvicorn src.api_server:app --host 0.0.0.0 --port 8000 --reload
```

5. **Start the web UI (optional):**
```bash
python run_web_ui.py
```

## Accessing the Service

### API Endpoints
- **Health Check:** http://localhost:8000/health
- **System Info:** http://localhost:8000/info
- **Statistics:** http://localhost:8000/stats
- **Performance:** http://localhost:8000/performance

### Web Interface
- **Web UI:** http://localhost:8081

### API Key
Use this API key for all authenticated requests:
```
AIzaSyAVBDGK6lP9SjFuAG0c3VxJ3Jly25LUBy0
```

## Testing the Service

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. System Information
```bash
curl -H "Authorization: Bearer AIzaSyAVBDGK6lP9SjFuAG0c3VxJ3Jly25LUBy0" \
     http://localhost:8000/info
```

### 3. Create Vector Database
```bash
curl -X POST http://localhost:8000/create \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer AIzaSyAVBDGK6lP9SjFuAG0c3VxJ3Jly25LUBy0" \
     -d '{"folder_path": "./pdfs"}'
```

### 4. Ask a Question
```bash
curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer AIzaSyAVBDGK6lP9SjFuAG0c3VxJ3Jly25LUBy0" \
     -d '{"question": "What is Qualcomm?", "max_results": 3, "include_sources": true}'
```

## Directory Structure

```
project/
├── src/                    # Source code
│   ├── api_server.py      # FastAPI server
│   ├── rag_system.py      # RAG logic
│   ├── pdf_processor.py   # PDF processing
│   └── utils.py           # Utilities
├── web-ui/                # Web interface
│   └── index.html         # Web UI
├── pdfs/                  # PDF documents
├── data/                  # Vector database storage
├── logs/                  # Log files
├── requirements.txt       # Python dependencies
├── run_local.py          # Automated setup script
├── run_web_ui.py         # Web UI server
└── LOCAL_SETUP.md        # This guide
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Make sure you're in the project root directory
   cd /path/to/your/project
   
   # Add src to Python path
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
   ```

2. **Port Already in Use**
   ```bash
   # Check what's using port 8000
   lsof -i :8000
   
   # Kill the process or use a different port
   python -m uvicorn src.api_server:app --host 0.0.0.0 --port 8001 --reload
   ```

3. **ChromaDB Issues**
   ```bash
   # Clear the database
   rm -rf data/chromadb
   
   # Restart the server
   python -m uvicorn src.api_server:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **API Key Issues**
   ```bash
   # Set environment variables
   export API_KEY="AIzaSyAVBDGK6lP9SjFuAG0c3VxJ3Jly25LUBy0"
   export GOOGLE_API_KEY="AIzaSyAVBDGK6lP9SjFuAG0c3VxJ3Jly25LUBy0"
   ```

### Performance Optimization

The system includes automatic performance monitoring:

- **Check performance:** http://localhost:8000/performance
- **View statistics:** http://localhost:8000/stats

The system will automatically optimize chunk size and overlap based on response times.

## Development

### Running in Development Mode
```bash
# Start with auto-reload
python -m uvicorn src.api_server:app --host 0.0.0.0 --port 8000 --reload

# Start web UI
python run_web_ui.py
```

### Adding PDF Documents
1. Place PDF files in the `pdfs/` directory
2. Create the vector database:
   ```bash
   curl -X POST http://localhost:8000/create \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer AIzaSyAVBDGK6lP9SjFuAG0c3VxJ3Jly25LUBy0" \
        -d '{"folder_path": "./pdfs"}'
   ```

### Logs
Check the logs for debugging:
```bash
tail -f logs/rag_service.log
```

## Stopping the Service

- **FastAPI Server:** Press `Ctrl+C` in the terminal
- **Web UI Server:** Press `Ctrl+C` in the terminal

## Next Steps

1. **Add PDF documents** to the `pdfs/` directory
2. **Create the vector database** using the `/create` endpoint
3. **Start asking questions** using the `/query` endpoint
4. **Use the web interface** at http://localhost:8081

## Support

If you encounter issues:
1. Check the logs in `logs/rag_service.log`
2. Verify all environment variables are set
3. Ensure Python 3.10+ is installed
4. Make sure all requirements are installed

The system is now ready to use without Docker! 🎉 