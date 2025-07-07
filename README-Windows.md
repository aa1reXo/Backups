# 🪟 Windows Deployment Guide - Qualcomm Linux RAG Q&A Service

This guide will help you deploy the Qualcomm Linux RAG Q&A Service on a Windows system.

## 📋 Prerequisites

### Required Software
1. **Docker Desktop for Windows**
   - Download: https://www.docker.com/products/docker-desktop/
   - Install and restart your computer
   - Ensure Docker Desktop is running (check system tray)

2. **Git for Windows**
   - Download: https://git-scm.com/download/win
   - Install with default settings

3. **PowerShell** (recommended) or Command Prompt
   - Run as Administrator if needed

### System Requirements
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 20GB free space
- **OS**: Windows 10/11 (64-bit)
- **Docker**: WSL2 backend (Docker Desktop will configure this)

## 🚀 Quick Start (Automated)

### Option 1: Use the Deployment Script
```powershell
# 1. Open PowerShell as Administrator
# 2. Navigate to the project directory
cd C:\path\to\Hkthon

# 3. Run the deployment script
.\deploy-windows.ps1
```

The script will:
- ✅ Check Docker installation
- ✅ Set environment variables
- ✅ Create necessary directories
- ✅ Build and start services
- ✅ Test the deployment
- ✅ Open the web interface

### Option 2: Manual Deployment
```powershell
# 1. Clone the repository
git clone <your-repo-url>
cd Hkthon

# 2. Set environment variables
$env:GEMINI_API_KEY="your_gemini_api_key"
$env:API_KEY="your_custom_api_key"  # Optional

# 3. Add PDF documents to pdfs/ directory

# 4. Build and start
docker-compose up --build -d
```

## 📁 Directory Structure
```
Hkthon/
├── deploy-windows.ps1    # Windows deployment script
├── docker-compose.yml    # Service configuration
├── Dockerfile           # Container definition
├── requirements.txt     # Python dependencies
├── src/                 # Application source code
├── pdfs/               # PDF documents (add your files here)
├── data/               # Vector database storage
├── logs/               # Application logs
└── web-ui/             # Web interface files
```

## 🔧 Configuration

### Environment Variables
```powershell
# Required
$env:GEMINI_API_KEY="your_gemini_api_key"

# Optional
$env:API_KEY="your_custom_api_key"  # Default: test_api_key
```

### Adding PDF Documents
1. Place your PDF files in the `pdfs/` directory
2. Restart the service: `docker-compose restart`

## 🧪 Testing

### 1. Service Health Check
```powershell
# Test basic connectivity
curl http://localhost:8000/

# Expected response:
# {"message": "Qualcomm Linux RAG Q&A Service", "version": "1.0.0", "status": "running"}
```

### 2. API Documentation
- Open browser: http://localhost:8000/docs
- Interactive API testing interface

### 3. Web Interface
- Open browser: http://localhost:8080
- User-friendly question interface

### 4. Command Line Testing
```powershell
# Test a query
curl -X POST "http://localhost:8000/query" `
  -H "Authorization: Bearer test_api_key" `
  -H "Content-Type: application/json" `
  -d '{
    "question": "What are the key features of 6G technology?",
    "max_results": 3,
    "include_sources": true
  }'
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Docker Desktop Not Running
```powershell
# Check Docker status
docker --version
docker ps

# If Docker is not running, start Docker Desktop from Start Menu
```

#### 2. Port Already in Use
```powershell
# Check what's using the ports
netstat -ano | findstr :8000
netstat -ano | findstr :8080

# Stop conflicting services or change ports in docker-compose.yml
```

#### 3. Permission Issues
```powershell
# Run PowerShell as Administrator
# Or check file permissions on pdfs/ directory
```

#### 4. Environment Variables Not Set
```powershell
# Check environment variables
echo $env:GEMINI_API_KEY
echo $env:API_KEY

# Set them if missing
$env:GEMINI_API_KEY="your_key"
$env:API_KEY="test_api_key"
```

#### 5. Service Not Responding
```powershell
# Check container status
docker-compose ps

# View logs
docker-compose logs -f

# Restart services
docker-compose restart
```

### Performance Issues

#### 1. Slow Startup
- Increase Docker Desktop memory allocation (8GB+ recommended)
- Ensure sufficient disk space (20GB+)

#### 2. Slow Responses
- Check internet connection (for Gemini API)
- Monitor Docker Desktop resource usage

## 📊 Monitoring

### View Logs
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f qualcomm-rag
```

### Check Resource Usage
```powershell
# Container resource usage
docker stats

# Disk usage
docker system df
```

### Service Statistics
```powershell
# Get service stats
curl -H "Authorization: Bearer test_api_key" http://localhost:8000/stats
```

## 🔄 Maintenance

### Update the Service
```powershell
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose up --build -d
```

### Backup Data
```powershell
# Backup vector database
copy data\ data-backup\

# Backup logs
copy logs\ logs-backup\
```

### Clean Up
```powershell
# Remove unused Docker resources
docker system prune -a

# Clear vector database
curl -X DELETE -H "Authorization: Bearer test_api_key" http://localhost:8000/clear-db
```

## 🌐 Access URLs

| Service | URL | Description |
|---------|-----|-------------|
| Web Interface | http://localhost:8080 | User-friendly Q&A interface |
| API Documentation | http://localhost:8000/docs | Interactive API docs |
| API Endpoint | http://localhost:8000 | REST API base URL |
| Health Check | http://localhost:8000/ | Service status |

## 📞 Support

If you encounter issues:

1. **Check the logs**: `docker-compose logs -f`
2. **Verify Docker Desktop**: Ensure it's running
3. **Check environment variables**: `echo $env:GEMINI_API_KEY`
4. **Restart services**: `docker-compose restart`
5. **Rebuild if needed**: `docker-compose up --build -d`

## 🎯 Next Steps

After successful deployment:

1. **Add your PDF documents** to the `pdfs/` directory
2. **Test the web interface** at http://localhost:8080
3. **Explore the API** at http://localhost:8000/docs
4. **Customize the system** by modifying configuration files
5. **Monitor performance** using the provided tools

---

**Happy Querying! 🚀** 