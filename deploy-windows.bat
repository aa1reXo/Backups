@echo off
echo 🚀 Qualcomm Linux RAG Q&A Service - Windows Deployment
echo ==================================================

REM Check if Docker is available
echo Checking Docker Desktop...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not available. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Desktop is running
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Desktop is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)
echo ✅ Docker Desktop is running

REM Set environment variables
echo Setting environment variables...
if "%GEMINI_API_KEY%"=="" (
    set /p GEMINI_API_KEY="Enter your Gemini API key: "
)

if "%API_KEY%"=="" (
    set API_KEY=test_api_key
)
echo ✅ Environment variables set

REM Create necessary directories
echo Creating directories...
if not exist "pdfs" mkdir pdfs
if not exist "data" mkdir data
if not exist "logs" mkdir logs
echo ✅ Directories created

REM Check for PDF files
dir /b pdfs\*.pdf >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  No PDF files found in pdfs directory
    echo    Please add your PDF documents to the pdfs folder
) else (
    echo ✅ PDF files found
)

REM Build and start services
echo Building and starting services...
docker-compose down >nul 2>&1
docker-compose up --build -d
if %errorlevel% neq 0 (
    echo ❌ Failed to start services
    pause
    exit /b 1
)
echo ✅ Services started successfully

REM Wait for services to be ready
echo Waiting for services to be ready...
timeout /t 30 /nobreak >nul

REM Test the service
echo Testing service...
curl -s http://localhost:8000/ >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Service is not responding yet. Please wait a moment and try again.
) else (
    echo ✅ Service is responding
)

REM Display access information
echo.
echo 🎉 Deployment Complete!
echo =====================
echo Service URLs:
echo   🌐 Web Interface: http://localhost:8080
echo   📚 API Documentation: http://localhost:8000/docs
echo   🔧 API Endpoint: http://localhost:8000
echo.
echo Useful Commands:
echo   View logs: docker-compose logs -f
echo   Stop services: docker-compose down
echo   Restart services: docker-compose restart
echo.

REM Open web interface
echo Opening web interface...
start http://localhost:8080

pause 