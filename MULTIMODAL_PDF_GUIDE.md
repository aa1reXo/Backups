# 📄 Multimodal PDF Processing System

## 🎯 **What We're Building**

A sophisticated PDF processing system that treats **each page as a separate document** and uses **OCR (Optical Character Recognition)** to extract text from scanned documents, images, and complex layouts.

## 🔄 **Current vs. New System**

### **Current System (Basic)**
```python
# Old approach - treats entire PDF as one document
pdf_processor = PDFProcessor()
chunks = pdf_processor.process_pdf_file("document.pdf")
# Result: One long text document split into chunks
```

### **New System (Multimodal)**
```python
# New approach - treats each page as separate document
multimodal_processor = MultimodalPDFProcessor()
pages = multimodal_processor.process_pdf_file("document.pdf")
# Result: List of pages, each with text + images + OCR
```

## 🚀 **Key Features**

### **1. Page-Level Processing**
- ✅ Each page = separate document
- ✅ Individual page metadata
- ✅ Page-specific chunking
- ✅ Page image extraction

### **2. OCR Capabilities**
- ✅ Extract text from scanned PDFs
- ✅ Handle complex layouts
- ✅ Multiple language support
- ✅ Image preprocessing for accuracy

### **3. Multimodal Content**
- ✅ Text extraction (direct + OCR)
- ✅ Embedded image extraction
- ✅ Page image capture
- ✅ Base64 encoding for storage

### **4. Advanced Processing**
- ✅ High-resolution image extraction (300-600 DPI)
- ✅ Image denoising and enhancement
- ✅ Configurable chunk sizes
- ✅ Overlapping chunks for context

## 📊 **Data Structure**

Each page produces this structure:

```json
{
  "doc_name": "document_name",
  "page_num": 0,
  "text_chunks": [
    {
      "chunk_id": "doc_page_0_0",
      "text": "Extracted text content...",
      "doc_name": "document_name",
      "page_num": 0,
      "chunk_index": 0,
      "word_count": 150,
      "token_count": 200,
      "content_type": "text"
    }
  ],
  "images": [
    {
      "image_index": 0,
      "image_data": "base64_encoded_image",
      "width": 800,
      "height": 600,
      "colorspace": 1,
      "format": "png"
    }
  ],
  "page_image": "base64_encoded_page_image",
  "ocr_text": "Text extracted via OCR",
  "has_text": true,
  "has_images": true
}
```

## 🛠 **Installation & Setup**

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Install Tesseract OCR**

**macOS:**
```bash
brew install tesseract
brew install tesseract-lang  # For additional languages
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-eng tesseract-ocr-fra  # Language packs
```

**Windows:**
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Add to PATH: `C:\Program Files\Tesseract-OCR`

### **3. Verify Installation**
```bash
tesseract --version
```

## 📝 **Usage Examples**

### **Basic Usage**
```python
from src.multimodal_pdf_processor import MultimodalPDFProcessor

# Initialize processor
processor = MultimodalPDFProcessor(
    chunk_size=1000,
    chunk_overlap=200,
    ocr_lang='eng',
    dpi=300,
    enable_ocr=True,
    enable_image_extraction=True
)

# Process a single PDF
pages = processor.process_pdf_file("document.pdf")

# Process all PDFs in a folder
all_pages = processor.process_pdf_folder("pdfs/")

# Get statistics
stats = processor.get_processing_stats(pages)
print(f"Processed {stats['total_pages']} pages")
```

### **Advanced Configuration**
```python
# Multi-language OCR
processor = MultimodalPDFProcessor(
    ocr_lang='eng+fra+spa',  # English + French + Spanish
    dpi=600,  # Higher resolution
    chunk_size=1500,  # Larger chunks
    chunk_overlap=300  # More overlap
)

# OCR-only mode (no image extraction)
processor = MultimodalPDFProcessor(
    enable_ocr=True,
    enable_image_extraction=False
)

# Text-only mode (no OCR)
processor = MultimodalPDFProcessor(
    enable_ocr=False,
    enable_image_extraction=True
)
```

## 🔧 **Configuration Options**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `chunk_size` | 1000 | Target words per chunk |
| `chunk_overlap` | 200 | Overlapping words between chunks |
| `ocr_lang` | 'eng' | OCR language(s) |
| `dpi` | 300 | Image resolution for extraction |
| `enable_ocr` | True | Enable OCR processing |
| `enable_image_extraction` | True | Extract embedded images |

## 🌍 **Supported Languages**

### **OCR Languages**
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

The system provides detailed statistics:

```python
stats = processor.get_processing_stats(pages)

# Available metrics:
# - total_pages: Number of pages processed
# - total_chunks: Total text chunks created
# - total_words: Total words extracted
# - total_tokens: Total tokens (for LLM context)
# - pages_with_text: Pages containing text
# - pages_with_images: Pages with embedded images
# - total_images: Total embedded images extracted
# - documents_processed: Number of PDF files
# - avg_chunk_size: Average words per chunk
```

## 🔍 **Processing Pipeline**

### **Step 1: Page Extraction**
```python
# Extract page as high-resolution image
page_image = processor.extract_page_as_image(pdf_doc, page_num)
```

### **Step 2: Text Extraction**
```python
# Try direct text extraction first
direct_text = page.get_text()

# If no text, perform OCR
if not direct_text:
    ocr_text = processor.perform_ocr_on_image(page_image)
```

### **Step 3: Image Extraction**
```python
# Extract embedded images
images = processor.extract_images_from_page(pdf_doc, page_num)
```

### **Step 4: Chunking**
```python
# Split text into overlapping chunks
chunks = processor.split_text_into_chunks(text, doc_name, page_num)
```

## 🧪 **Testing**

Run the test script to verify functionality:

```bash
python test_multimodal_processor.py
```

This will:
- ✅ Test processor initialization
- ✅ Verify OCR capabilities
- ✅ Show processing statistics
- ✅ Save results to JSON file

## 🚨 **Common Issues & Solutions**

### **1. Tesseract Not Found**
```
Error: tesseract is not installed or not in PATH
```
**Solution:** Install Tesseract and add to PATH

### **2. OCR Accuracy Issues**
```
Poor OCR results on complex layouts
```
**Solutions:**
- Increase DPI: `dpi=600`
- Use specific PSM modes
- Preprocess images manually

### **3. Memory Issues**
```
Out of memory with large PDFs
```
**Solutions:**
- Process pages individually
- Reduce DPI: `dpi=150`
- Disable image extraction

### **4. Language Pack Missing**
```
Error: eng language pack not found
```
**Solution:** Install language packs for your OS

## 🔮 **Future Enhancements**

### **Planned Features**
- [ ] Table detection and extraction
- [ ] Form field recognition
- [ ] Handwriting recognition
- [ ] Mathematical equation OCR
- [ ] Diagram and chart analysis
- [ ] PDF annotation extraction

### **Integration Possibilities**
- [ ] ChromaDB vector storage
- [ ] Gemini Vision API integration
- [ ] Real-time processing
- [ ] Batch processing optimization

## 📚 **API Reference**

### **MultimodalPDFProcessor Class**

#### **Methods:**
- `process_pdf_file(pdf_path)` - Process single PDF
- `process_pdf_folder(folder_path)` - Process folder of PDFs
- `process_single_page(pdf_doc, page_num, doc_name)` - Process one page
- `get_processing_stats(pages)` - Get statistics
- `perform_ocr_on_image(image)` - OCR on image
- `extract_page_as_image(pdf_doc, page_num)` - Extract page image
- `extract_images_from_page(pdf_doc, page_num)` - Extract embedded images

#### **Properties:**
- `chunk_size` - Target words per chunk
- `chunk_overlap` - Overlapping words
- `ocr_lang` - OCR language
- `dpi` - Image resolution
- `enable_ocr` - OCR enabled flag
- `enable_image_extraction` - Image extraction flag

## 🎯 **Use Cases**

### **1. Document Digitization**
- Scan physical documents
- Extract text via OCR
- Store in searchable format

### **2. Research Papers**
- Extract text and figures
- Process each page separately
- Enable semantic search

### **3. Legal Documents**
- Handle complex layouts
- Extract text and images
- Maintain page structure

### **4. Technical Manuals**
- Process diagrams and text
- Extract embedded images
- Create searchable knowledge base

---

**This multimodal system transforms PDF processing from simple text extraction to a comprehensive document understanding platform! 🚀** 