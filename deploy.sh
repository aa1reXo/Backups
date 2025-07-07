#!/bin/bash

# Qualcomm Linux RAG Q&A Service Deployment Script

set -e

echo "🚀 Deploying Qualcomm Linux RAG Q&A Service..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
print_status "Creating directories..."
mkdir -p data logs pdfs

# Check environment variables
if [ -z "$API_KEY" ]; then
    print_warning "API_KEY not set. Using default value."
    export API_KEY="default_api_key_$(date +%s)"
fi

if [ -z "$QGENIE_API_KEY" ]; then
    print_warning "QGENIE_API_KEY not set. Please set it for LLM functionality."
    export QGENIE_API_KEY="test_qgenie_key"
fi

# Build Docker image
print_status "Building Docker image..."
docker build -t qualcomm-rag-service .

if [ $? -eq 0 ]; then
    print_status "Docker image built successfully!"
else
    print_error "Failed to build Docker image."
    exit 1
fi

# Start services
print_status "Starting services..."
docker-compose up -d

# Wait for service to be ready
print_status "Waiting for service to be ready..."
sleep 10

# Check if service is running
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "Service is running successfully!"
    echo ""
    echo "📋 Service Information:"
    echo "  - API Endpoint: http://localhost:8000"
    echo "  - Web UI: http://localhost:8080 (if enabled)"
    echo "  - Health Check: http://localhost:8000/health"
    echo "  - API Documentation: http://localhost:8000/docs"
    echo ""
    echo "🔑 API Key: $API_KEY"
    echo ""
    echo "📁 Directories:"
    echo "  - PDFs: ./pdfs (mount to /local/mnt/workspace/sparq25)"
    echo "  - Data: ./data (vector database)"
    echo "  - Logs: ./logs (application logs)"
    echo ""
    echo "🚀 Next steps:"
    echo "  1. Place your Qualcomm Linux PDF files in the ./pdfs directory"
    echo "  2. Create the vector database:"
    echo "     curl -X POST http://localhost:8000/create \\"
    echo "          -H 'Authorization: Bearer $API_KEY' \\"
    echo "          -H 'Content-Type: application/json' \\"
    echo "          -d '{\"folder_path\": \"/local/mnt/workspace/sparq25\"}'"
    echo "  3. Start asking questions!"
    echo ""
    print_status "Deployment completed successfully! 🎉"
else
    print_error "Service failed to start properly."
    echo "Check logs with: docker-compose logs"
    exit 1
fi 