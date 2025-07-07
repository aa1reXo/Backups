# Windows Deployment Script for Qualcomm Linux RAG Q&A Service
# Run this script as Administrator

Write-Host "🚀 Qualcomm Linux RAG Q&A Service - Windows Deployment" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Check if Docker is running
Write-Host "Checking Docker Desktop..." -ForegroundColor Yellow
try {
    docker --version | Out-Null
    Write-Host "✅ Docker is available" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not available. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if Docker Desktop is running
try {
    docker ps | Out-Null
    Write-Host "✅ Docker Desktop is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Desktop is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Set environment variables
Write-Host "Setting environment variables..." -ForegroundColor Yellow

# Check if GEMINI_API_KEY is already set
if (-not $env:GEMINI_API_KEY) {
    $env:GEMINI_API_KEY = Read-Host "Enter your Gemini API key"
}

# Set default API key if not provided
if (-not $env:API_KEY) {
    $env:API_KEY = "test_api_key"
}

Write-Host "✅ Environment variables set" -ForegroundColor Green

# Create necessary directories
Write-Host "Creating directories..." -ForegroundColor Yellow
if (-not (Test-Path "pdfs")) {
    New-Item -ItemType Directory -Path "pdfs" | Out-Null
    Write-Host "✅ Created pdfs directory" -ForegroundColor Green
}

if (-not (Test-Path "data")) {
    New-Item -ItemType Directory -Path "data" | Out-Null
    Write-Host "✅ Created data directory" -ForegroundColor Green
}

if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
    Write-Host "✅ Created logs directory" -ForegroundColor Green
}

# Check if PDFs are present
$pdfFiles = Get-ChildItem -Path "pdfs" -Filter "*.pdf" -ErrorAction SilentlyContinue
if ($pdfFiles.Count -eq 0) {
    Write-Host "⚠️  No PDF files found in pdfs directory" -ForegroundColor Yellow
    Write-Host "   Please add your PDF documents to the pdfs folder" -ForegroundColor Yellow
} else {
    Write-Host "✅ Found $($pdfFiles.Count) PDF file(s)" -ForegroundColor Green
}

# Build and start services
Write-Host "Building and starting services..." -ForegroundColor Yellow
try {
    docker-compose down 2>$null
    docker-compose up --build -d
    Write-Host "✅ Services started successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to start services" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

# Wait for services to be ready
Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Test the service
Write-Host "Testing service..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/" -Method Get
    Write-Host "✅ Service is responding: $($response.message)" -ForegroundColor Green
} catch {
    Write-Host "❌ Service is not responding yet. Please wait a moment and try again." -ForegroundColor Red
}

# Display access information
Write-Host ""
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "=====================" -ForegroundColor Green
Write-Host "Service URLs:" -ForegroundColor Cyan
Write-Host "  🌐 Web Interface: http://localhost:8080" -ForegroundColor White
Write-Host "  📚 API Documentation: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  🔧 API Endpoint: http://localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "Useful Commands:" -ForegroundColor Cyan
Write-Host "  View logs: docker-compose logs -f" -ForegroundColor White
Write-Host "  Stop services: docker-compose down" -ForegroundColor White
Write-Host "  Restart services: docker-compose restart" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to open the web interface..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Open web interface
Start-Process "http://localhost:8080" 