@echo off
echo 🔍 Qualcomm Linux RAG Q&A Service - Local Setup
echo ================================================

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found

REM Install requirements
echo 📦 Installing requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install requirements
    pause
    exit /b 1
)

echo ✅ Requirements installed

REM Create directories
echo 📁 Creating directories...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "pdfs" mkdir pdfs
if not exist "local\mnt\workspace\sparq25" mkdir "local\mnt\workspace\sparq25"

echo ✅ Directories created

REM Set environment variables
echo 🔧 Setting environment variables...
set API_KEY=AIzaSyAVBDGK6lP9SjFuAG0c3VxJ3Jly25LUBy0
set GOOGLE_API_KEY=AIzaSyAVBDGK6lP9SjFuAG0c3VxJ3Jly25LUBy0
set CHROMA_DB_IMPL=duckdb+parquet
set PERSIST_DIRECTORY=./data

echo ✅ Environment variables set

echo.
echo 🚀 Starting FastAPI server...
echo 📍 Server will be available at: http://localhost:8000
echo 📍 Web UI will be available at: http://localhost:8081
echo 🔑 API Key: AIzaSyAVBDGK6lP9SjFuAG0c3VxJ3Jly25LUBy0
echo.
echo 💡 To stop the server, press Ctrl+C
echo.

REM Start the server
python -m uvicorn src.api_server:app --host 0.0.0.0 --port 8000 --reload

pause 