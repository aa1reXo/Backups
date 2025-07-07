# 🔍 Multimodal RAG Q&A Service

A sophisticated PDF processing system that treats **each page as a separate document** and uses **OCR (Optical Character Recognition)** to extract text from scanned documents, images, and complex layouts.

## 🚀 **Key Features**

### **Multimodal PDF Processing**
- ✅ **Page-level processing** - Each page = separate document
- ✅ **OCR capabilities** - Extract text from scanned PDFs
- ✅ **Image extraction** - Extract embedded images and page images
- ✅ **High-resolution processing** - 300-600 DPI image extraction
- ✅ **Multi-language support** - English, French, Spanish, German, etc.
- ✅ **Image preprocessing** - Denoising and contrast enhancement

### **Advanced RAG System**
- ✅ **ChromaDB integration** - Vector database for semantic search
- ✅ **Google Gemini Pro** - State-of-the-art LLM integration
- ✅ **Sentence transformers** - High-quality embeddings
- ✅ **Overlapping chunks** - Context preservation
- ✅ **Metadata tracking** - Page numbers, image counts, similarity scores

### **Complete API**
- ✅ **Health monitoring** - System status and uptime
- ✅ **Statistics tracking** - Query counts and response times
- ✅ **Database management** - Create, query, and manage collections
- ✅ **Context retrieval** - Get relevant documents without LLM
- ✅ **Full query system** - Ask questions and get answers with sources

## 📊 **System Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PDF Input     │    │  Multimodal     │    │   ChromaDB      │
│   (Text + OCR)  │───▶│  Processor      │───▶│   Vector DB     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   FastAPI       │    │   Google Gemini │
                       │   REST API      │◄───│   Pro LLM       │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Web UI        │
                       │   (Optional)    │
                       └─────────────────┘
```

## 🛠 **Installation**

### **1. Prerequisites**
```bash
# Install Tesseract OCR
chmod +x install_tesseract.sh
./install_tesseract.sh

# Or install manually:
# macOS: brew install tesseract
# Ubuntu: sudo apt-get install tesseract-ocr
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
```

### **2. Python Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Environment Setup**
```bash
# Create .env file
cp .env.example .env

# Add your Google API key
echo "GOOGLE_API_KEY=your_api_key_here" >> .env
```

### **4. Docker Setup (Recommended)**
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or run individual containers
docker build -t multimodal-rag .
docker run -p 8000:8000 multimodal-rag
```

## 📋 **API Endpoints**

### **Core Endpoints**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health check |
| `/info` | GET | System information |
| `/stats` | GET | Performance statistics |
| `/create` | POST | Create vector database from PDFs |
| `/context` | POST | Get retrieval context |
| `/query` | POST | Ask questions and get answers |

### **Management Endpoints**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/collections` | GET | List all collections |
| `/collections/{name}` | GET | Get collection info |
| `/collections/{name}` | DELETE | Delete collection |

### **Example Usage**

#### **Create Vector Database**
```bash
curl -X POST "http://localhost:8000/create" \
  -H "Content-Type: application/json" \
  -d '{"folder_path": "/app/pdfs"}'
```

#### **Ask a Question**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the key features?",
    "max_results": 5,
    "include_sources": true
  }'
```

#### **Get Context Only**
```bash
curl -X POST "http://localhost:8000/context" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic?"}'
```

## 🧪 **Testing**

### **1. Test API Endpoints**
```bash
python test_api_endpoints.py
```

### **2. Test Multimodal Processor**
```bash
python test_multimodal_processor.py
```

### **3. Test Integration**
```bash
python integrate_multimodal_rag.py
```

## 🌐 **Web Interface**

Access the web interface at `http://localhost:8080` (if using Docker Compose) or serve it manually:

```bash
# Serve web interface
python -m http.server 8080 --directory web-ui
```

### **Web Interface Features**
- ✅ **Query Interface** - Ask questions with real-time responses
- ✅ **Database Creation** - Upload and process PDFs
- ✅ **Context Retrieval** - Get relevant documents without LLM
- ✅ **System Monitoring** - View statistics and system info
- ✅ **Responsive Design** - Works on desktop and mobile

## 📊 **Data Processing Pipeline**

### **1. PDF Processing**
```python
# Each page becomes a separate document
pages = multimodal_processor.process_pdf_file("document.pdf")

# Each page contains:
{
    "doc_name": "document",
    "page_num": 0,
    "text_chunks": [...],      # Text content
    "images": [...],           # Embedded images
    "page_image": "base64",    # Page as image
    "ocr_text": "...",         # OCR extracted text
    "has_text": true,
    "has_images": true
}
```

### **2. Vector Storage**
```python
# Documents are stored with rich metadata
{
    "doc_name": "document",
    "page_num": 0,
    "chunk_index": 0,
    "content_type": "text",
    "has_images": true,
    "image_count": 2,
    "word_count": 150,
    "token_count": 200
}
```

### **3. Query Processing**
```python
# Semantic search finds relevant documents
results = rag_service.query_collection(
    query="What are the key features?",
    collection_name="default",
    n_results=5
)

# LLM generates answer with context
answer = llm_service.generate_response(prompt_with_context)
```

## 🔧 **Configuration**

### **Multimodal Processor Settings**
```python
processor = MultimodalPDFProcessor(
    chunk_size=1000,           # Words per chunk
    chunk_overlap=200,         # Overlapping words
    ocr_lang='eng',           # OCR language
    dpi=300,                  # Image resolution
    enable_ocr=True,          # Enable OCR
    enable_image_extraction=True  # Extract images
)
```

### **Supported Languages**
- `eng` - English
- `fra` - French  
- `spa` - Spanish
- `deu` - German
- `ita` - Italian
- `por` - Portuguese
- `rus` - Russian
- `chi_sim` - Chinese Simplified
- `jpn` - Japanese
- `kor` - Korean

### **Multi-language Support**
```python
# Multiple languages
processor = MultimodalPDFProcessor(ocr_lang='eng+fra+spa')
```

## 📈 **Performance Statistics**

The system tracks comprehensive statistics:

```json
{
    "total_pages": 150,
    "total_chunks": 450,
    "total_words": 45000,
    "total_tokens": 60000,
    "pages_with_text": 145,
    "pages_with_images": 80,
    "total_images": 200,
    "documents_processed": 10,
    "avg_chunk_size": 100.0,
    "ocr_enabled": true,
    "image_extraction_enabled": true
}
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Tesseract Not Found**
```bash
# Check installation
tesseract --version

# Install if missing
./install_tesseract.sh
```

#### **2. OCR Accuracy Issues**
```python
# Increase DPI for better accuracy
processor = MultimodalPDFProcessor(dpi=600)

# Use specific language
processor = MultimodalPDFProcessor(ocr_lang='eng+fra')
```

#### **3. Memory Issues**
```python
# Reduce DPI for large PDFs
processor = MultimodalPDFProcessor(dpi=150)

# Disable image extraction
processor = MultimodalPDFProcessor(enable_image_extraction=False)
```

#### **4. API Connection Issues**
```bash
# Check if server is running
curl http://localhost:8000/health

# Check logs
docker-compose logs multimodal-rag-service
```

## 🔮 **Future Enhancements**

### **Planned Features**
- [ ] **Table detection** - Extract and process tables
- [ ] **Form recognition** - Identify and extract form fields
- [ ] **Handwriting OCR** - Recognize handwritten text
- [ ] **Mathematical equations** - OCR for mathematical content
- [ ] **Diagram analysis** - Process charts and diagrams
- [ ] **PDF annotations** - Extract comments and highlights

### **Integration Possibilities**
- [ ] **Gemini Vision API** - Advanced image understanding
- [ ] **Real-time processing** - Stream PDF processing
- [ ] **Batch optimization** - Parallel processing
- [ ] **Cloud deployment** - AWS, GCP, Azure support

## 📚 **Documentation**

- 📖 **[Multimodal PDF Guide](MULTIMODAL_PDF_GUIDE.md)** - Detailed processing guide
- 📖 **[Windows Deployment](README-Windows.md)** - Windows setup instructions
- 📖 **[API Documentation](http://localhost:8000/docs)** - Interactive API docs
- 📖 **[Test Scripts](test_api_endpoints.py)** - Comprehensive testing

## 🤝 **Contributing**

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests**
5. **Submit a pull request**

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Tesseract OCR** - Open-source OCR engine
- **Google Gemini** - Advanced language model
- **ChromaDB** - Vector database
- **FastAPI** - Modern web framework
- **PyMuPDF** - PDF processing library

---

**🎉 This multimodal system transforms PDF processing from simple text extraction to a comprehensive document understanding platform!** 