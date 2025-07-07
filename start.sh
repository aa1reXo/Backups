#!/bin/bash

# Set the API key directly
export API_KEY="AIzaSyAVBDGK6lP9SjFuAG0c3VxJ3Jly25LUBy0"
export GOOGLE_API_KEY="AIzaSyAVBDGK6lP9SjFuAG0c3VxJ3Jly25LUBy0"

# Create necessary directories
mkdir -p /app/data
mkdir -p /app/logs
mkdir -p /local/mnt/workspace/sparq25

echo "Starting Qualcomm Linux RAG Q&A Service..."

# Run basic tests first (only if not in production)
if [ "$ENVIRONMENT" != "production" ]; then
    echo "Running basic functionality tests..."
    python test_basic.py
    if [ $? -ne 0 ]; then
        echo "Basic tests failed! Continuing anyway..."
    else
        echo "Basic tests passed!"
    fi
fi

echo "Starting FastAPI server..."

# Start the FastAPI server using the correct entry point
exec uvicorn src.api_server:app --host 0.0.0.0 --port 8000 --reload 
