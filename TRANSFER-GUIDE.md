# 📦 Transfer Guide: Qualcomm Linux RAG Q&A Service to Windows

This guide will help you transfer and deploy the RAG system on a Windows machine.

## 🎯 **What You're Transferring**

### **Core Application**
- ✅ **RAG System**: Vector search + Gemini LLM integration
- ✅ **PDF Processor**: Text extraction and chunking
- ✅ **FastAPI Backend**: REST API with authentication
- ✅ **Web Interface**: User-friendly Q&A interface
- ✅ **Docker Configuration**: Containerized deployment

### **Key Features**
- 🔍 **Semantic Search**: Find relevant context from PDFs
- 🤖 **AI-Powered Answers**: Google Gemini generates responses
- 📊 **Source Attribution**: See which documents were used
- 🌐 **Web Interface**: Easy-to-use browser interface
- 🔧 **REST API**: Programmatic access

## 📋 **Windows System Requirements**

### **Minimum Requirements**
- **OS**: Windows 10/11 (64-bit)
- **RAM**: 4GB (8GB recommended)
- **Storage**: 20GB free space
- **Internet**: For Docker images and Gemini API

### **Required Software**
1. **Docker Desktop for Windows**
   - Download: https://www.docker.com/products/docker-desktop/
   - Install and restart computer

2. **Git for Windows**
   - Download: https://git-scm.com/download/win
   - Install with defaults

## 🚀 **Transfer Process**

### **Step 1: Prepare the Source (Current System)**
```bash
# On your current system, ensure everything is working
docker-compose ps
curl http://localhost:8000/

# Create a clean copy of the project
cp -r Hkthon Hkthon-windows-transfer
cd Hkthon-windows-transfer

# Remove any system-specific files
rm -rf data/* logs/*
```

### **Step 2: Transfer to Windows**

#### **Option A: Git Repository (Recommended)**
```bash
# Push to a Git repository
git add .
git commit -m "Windows-ready version"
git push origin main

# On Windows, clone the repository
git clone <your-repo-url>
cd Hkthon
```

#### **Option B: Direct File Transfer**
- Copy the entire `Hkthon` folder to Windows
- Use USB drive, cloud storage, or network transfer
- Ensure all files are transferred intact

### **Step 3: Windows Deployment**

#### **Quick Start (Automated)**
```powershell
# Open PowerShell as Administrator
cd C:\path\to\Hkthon

# Run the deployment script
.\deploy-windows.ps1
```

#### **Manual Deployment**
```powershell
# Set environment variables
$env:GEMINI_API_KEY="your_gemini_api_key"
$env:API_KEY="test_api_key"

# Build and start
docker-compose up --build -d
```

## 📁 **Files Being Transferred**

### **Core Application Files**
```
Hkthon/
├── src/                    # Application source code
│   ├── main.py            # FastAPI application
│   ├── rag_system.py      # RAG system implementation
│   ├── pdf_processor.py   # PDF processing
│   └── utils.py           # Utility functions
├── web-ui/                # Web interface
│   └── index.html         # User interface
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container definition
├── docker-compose.yml    # Service orchestration
└── start.sh              # Startup script
```

### **Windows-Specific Files**
```
Hkthon/
├── deploy-windows.ps1     # PowerShell deployment script
├── deploy-windows.bat     # Command Prompt deployment script
├── README-Windows.md      # Windows-specific documentation
└── TRANSFER-GUIDE.md      # This guide
```

### **Configuration Files**
```
Hkthon/
├── pdfs/                  # PDF documents (add your files)
├── data/                  # Vector database (created automatically)
└── logs/                  # Application logs (created automatically)
```

## 🧪 **Testing on Windows**

### **1. Health Check**
```powershell
# Test basic connectivity
curl http://localhost:8000/

# Expected: {"message": "Qualcomm Linux RAG Q&A Service", "version": "1.0.0", "status": "running"}
```

### **2. Web Interface**
- Open: http://localhost:8080
- Type a question and test the system

### **3. API Testing**
```powershell
# Test query
curl -X POST "http://localhost:8000/query" `
  -H "Authorization: Bearer test_api_key" `
  -H "Content-Type: application/json" `
  -d '{
    "question": "What are the key features of 6G technology?",
    "max_results": 3,
    "include_sources": true
  }'
```

### **4. Service Statistics**
```powershell
curl -H "Authorization: Bearer test_api_key" http://localhost:8000/stats
```

## 🔧 **Configuration Options**

### **Environment Variables**
```powershell
# Required
$env:GEMINI_API_KEY="your_gemini_api_key"

# Optional
$env:API_KEY="your_custom_api_key"  # Default: test_api_key
```

### **Customizing the System**
- **Change ports**: Edit `docker-compose.yml`
- **Add PDFs**: Place files in `pdfs/` directory
- **Modify models**: Edit `src/rag_system.py`
- **Customize UI**: Edit `web-ui/index.html`

## 🛠️ **Troubleshooting**

### **Common Windows Issues**

#### **1. Docker Desktop Not Running**
```powershell
# Check Docker status
docker --version
docker ps

# Start Docker Desktop from Start Menu if needed
```

#### **2. Permission Issues**
```powershell
# Run PowerShell as Administrator
# Or check file permissions
```

#### **3. Port Conflicts**
```powershell
# Check port usage
netstat -ano | findstr :8000
netstat -ano | findstr :8080

# Change ports in docker-compose.yml if needed
```

#### **4. Environment Variables**
```powershell
# Check if set
echo $env:GEMINI_API_KEY

# Set if missing
$env:GEMINI_API_KEY="your_key"
```

### **Performance Optimization**
- **Increase Docker memory**: 8GB+ recommended
- **Use SSD storage**: Faster vector database access
- **Good internet**: For Gemini API calls

## 📊 **Monitoring & Maintenance**

### **View Logs**
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f qualcomm-rag
```

### **Resource Usage**
```powershell
# Container stats
docker stats

# Disk usage
docker system df
```

### **Backup & Restore**
```powershell
# Backup vector database
copy data\ data-backup\

# Restore
copy data-backup\ data\
```

## 🌐 **Access URLs**

| Service | URL | Description |
|---------|-----|-------------|
| Web Interface | http://localhost:8080 | User-friendly Q&A |
| API Docs | http://localhost:8000/docs | Interactive API testing |
| API Endpoint | http://localhost:8000 | REST API |
| Health Check | http://localhost:8000/ | Service status |

## 🎯 **Next Steps After Transfer**

1. **Add your PDF documents** to the `pdfs/` directory
2. **Test the web interface** at http://localhost:8080
3. **Explore the API** at http://localhost:8000/docs
4. **Customize the system** for your needs
5. **Set up monitoring** and logging
6. **Configure backups** for the vector database

## 📞 **Support**

If you encounter issues:

1. **Check logs**: `docker-compose logs -f`
2. **Verify Docker**: Ensure Docker Desktop is running
3. **Check environment**: `echo $env:GEMINI_API_KEY`
4. **Restart services**: `docker-compose restart`
5. **Rebuild if needed**: `docker-compose up --build -d`

---

## ✅ **Transfer Checklist**

- [ ] Docker Desktop installed on Windows
- [ ] Git installed on Windows
- [ ] Project files transferred
- [ ] Environment variables set
- [ ] PDF documents added
- [ ] Services started successfully
- [ ] Web interface accessible
- [ ] API responding correctly
- [ ] Test queries working
- [ ] Logs showing no errors

**🎉 Your RAG system is now ready on Windows!** 