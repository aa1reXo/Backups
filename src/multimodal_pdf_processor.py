import os
import re
import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
import pytesseract
from typing import List, Dict, Any, Tuple, Optional
from loguru import logger
from .utils import count_tokens, create_chunk_id
import base64
import io

class MultimodalPDFProcessor:
    def __init__(self, 
                 chunk_size: int = 1000, 
                 chunk_overlap: int = 200,
                 ocr_lang: str = 'eng',
                 dpi: int = 300,
                 enable_ocr: bool = True,
                 enable_image_extraction: bool = True):
        """
        Initialize Multimodal PDF processor
        
        Args:
            chunk_size: Target number of words per chunk
            chunk_overlap: Number of overlapping words between chunks
            ocr_lang: OCR language (eng, fra, spa, etc.)
            dpi: Resolution for image extraction
            enable_ocr: Whether to perform OCR on images
            enable_image_extraction: Whether to extract images
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.ocr_lang = ocr_lang
        self.dpi = dpi
        self.enable_ocr = enable_ocr
        self.enable_image_extraction = enable_image_extraction
        
        # Configure OCR
        if self.enable_ocr:
            try:
                # Set OCR config for better accuracy
                self.ocr_config = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,;:!?()[]{}"\'-_+=<>/\\|@#$%^&*~`'
            except Exception as e:
                logger.warning(f"OCR not available: {e}")
                self.enable_ocr = False
    
    def extract_page_as_image(self, pdf_doc, page_num: int) -> Optional[np.ndarray]:
        """Extract a page as high-resolution image"""
        try:
            page = pdf_doc[page_num]
            
            # Set transformation matrix for high DPI
            mat = fitz.Matrix(self.dpi/72, self.dpi/72)
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to numpy array
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            img_array = np.array(img)
            
            return img_array
        except Exception as e:
            logger.error(f"Error extracting page {page_num} as image: {e}")
            return None
    
    def perform_ocr_on_image(self, image: np.ndarray) -> str:
        """Perform OCR on image and return text"""
        try:
            if not self.enable_ocr:
                return ""
            
            # Convert to grayscale for better OCR
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image
            
            # Apply preprocessing for better OCR
            # Denoise
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Enhance contrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(denoised)
            
            # Perform OCR
            text = pytesseract.image_to_string(enhanced, 
                                             lang=self.ocr_lang,
                                             config=self.ocr_config)
            
            return text.strip()
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return ""
    
    def extract_images_from_page(self, pdf_doc, page_num: int) -> List[Dict[str, Any]]:
        """Extract embedded images from a page"""
        if not self.enable_image_extraction:
            return []
        
        try:
            page = pdf_doc[page_num]
            image_list = page.get_images()
            
            images = []
            for img_index, img in enumerate(image_list):
                try:
                    # Get image data
                    xref = img[0]
                    pix = fitz.Pixmap(pdf_doc, xref)
                    
                    if pix.n - pix.alpha < 4:  # GRAY or RGB
                        img_data = pix.tobytes("png")
                        
                        # Convert to base64 for storage
                        img_base64 = base64.b64encode(img_data).decode('utf-8')
                        
                        images.append({
                            "image_index": img_index,
                            "image_data": img_base64,
                            "width": pix.width,
                            "height": pix.height,
                            "colorspace": pix.colorspace.n,
                            "format": "png"
                        })
                    
                    pix = None  # Free memory
                    
                except Exception as e:
                    logger.warning(f"Error extracting image {img_index} from page {page_num}: {e}")
                    continue
            
            return images
        except Exception as e:
            logger.error(f"Error extracting images from page {page_num}: {e}")
            return []
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep technical terms
        text = re.sub(r'[^\w\s\-\.\,\;\:\!\?\(\)\[\]\{\}\+\=\*\&\^\%\$\#\@]', '', text)
        
        # Normalize line breaks
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        return text.strip()
    
    def split_text_into_chunks(self, text: str, doc_name: str, page_num: int) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks"""
        if not text:
            return []
            
        # Clean text
        text = self.clean_text(text)
        words = text.split()
        
        if len(words) <= self.chunk_size:
            return [{
                "chunk_id": create_chunk_id(f"{doc_name}_page_{page_num}", 0),
                "text": text,
                "doc_name": doc_name,
                "page_num": page_num,
                "chunk_index": 0,
                "word_count": len(words),
                "token_count": count_tokens(text),
                "content_type": "text"
            }]
        
        chunks = []
        chunk_index = 0
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            
            if len(chunk_text.strip()) < 50:  # Skip very short chunks
                continue
                
            chunks.append({
                "chunk_id": create_chunk_id(f"{doc_name}_page_{page_num}", chunk_index),
                "text": chunk_text,
                "doc_name": doc_name,
                "page_num": page_num,
                "chunk_index": chunk_index,
                "word_count": len(chunk_words),
                "token_count": count_tokens(chunk_text),
                "content_type": "text"
            })
            
            chunk_index += 1
            
            # Stop if we've covered all words
            if i + self.chunk_size >= len(words):
                break
        
        return chunks
    
    def process_single_page(self, pdf_doc, page_num: int, doc_name: str) -> Dict[str, Any]:
        """Process a single page as a multimodal document"""
        logger.info(f"Processing page {page_num} of {doc_name}")
        
        page_data = {
            "doc_name": doc_name,
            "page_num": page_num,
            "text_chunks": [],
            "images": [],
            "page_image": None,
            "ocr_text": "",
            "has_text": False,
            "has_images": False
        }
        
        # 1. Extract page as image
        page_image = self.extract_page_as_image(pdf_doc, page_num)
        if page_image is not None:
            page_data["page_image"] = base64.b64encode(
                cv2.imencode('.png', page_image)[1]
            ).decode('utf-8')
        
        # 2. Extract embedded images
        if self.enable_image_extraction:
            images = self.extract_images_from_page(pdf_doc, page_num)
            page_data["images"] = images
            page_data["has_images"] = len(images) > 0
        
        # 3. Try to extract text directly first
        try:
            page = pdf_doc[page_num]
            direct_text = page.get_text()
            if direct_text.strip():
                page_data["has_text"] = True
                page_data["text_chunks"] = self.split_text_into_chunks(
                    direct_text, doc_name, page_num
                )
        except Exception as e:
            logger.warning(f"Could not extract direct text from page {page_num}: {e}")
        
        # 4. If no direct text, perform OCR
        if not page_data["has_text"] and self.enable_ocr and page_image is not None:
            ocr_text = self.perform_ocr_on_image(page_image)
            if ocr_text.strip():
                page_data["ocr_text"] = ocr_text
                page_data["has_text"] = True
                page_data["text_chunks"] = self.split_text_into_chunks(
                    ocr_text, doc_name, page_num
                )
                logger.info(f"OCR extracted {len(ocr_text.split())} words from page {page_num}")
        
        return page_data
    
    def process_pdf_file(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Process a single PDF file, treating each page as a separate document"""
        doc_name = os.path.basename(pdf_path).replace('.pdf', '')
        
        logger.info(f"Processing PDF: {pdf_path}")
        
        try:
            pdf_doc = fitz.open(pdf_path)
            total_pages = len(pdf_doc)
            
            all_pages = []
            
            for page_num in range(total_pages):
                try:
                    page_data = self.process_single_page(pdf_doc, page_num, doc_name)
                    all_pages.append(page_data)
                    
                    logger.info(f"Page {page_num + 1}/{total_pages}: "
                              f"Text chunks: {len(page_data['text_chunks'])}, "
                              f"Images: {len(page_data['images'])}")
                    
                except Exception as e:
                    logger.error(f"Error processing page {page_num}: {e}")
                    continue
            
            pdf_doc.close()
            
            logger.info(f"Processed {len(all_pages)} pages from {pdf_path}")
            return all_pages
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            return []
    
    def process_pdf_folder(self, folder_path: str) -> List[Dict[str, Any]]:
        """Process all PDF files in a folder"""
        all_pages = []
        
        if not os.path.exists(folder_path):
            logger.error(f"Folder not found: {folder_path}")
            return []
        
        # Find all PDF files
        pdf_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
        
        logger.info(f"Found {len(pdf_files)} PDF files in {folder_path}")
        
        # Process each PDF
        for pdf_path in pdf_files:
            try:
                pages = self.process_pdf_file(pdf_path)
                all_pages.extend(pages)
            except Exception as e:
                logger.error(f"Error processing {pdf_path}: {e}")
                continue
        
        logger.info(f"Total pages processed: {len(all_pages)}")
        return all_pages
    
    def get_processing_stats(self, pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about processed pages"""
        if not pages:
            return {
                "total_pages": 0,
                "total_chunks": 0,
                "total_words": 0,
                "total_tokens": 0,
                "pages_with_text": 0,
                "pages_with_images": 0,
                "total_images": 0,
                "documents_processed": 0
            }
        
        total_chunks = sum(len(page["text_chunks"]) for page in pages)
        total_words = sum(
            sum(chunk["word_count"] for chunk in page["text_chunks"]) 
            for page in pages
        )
        total_tokens = sum(
            sum(chunk["token_count"] for chunk in page["text_chunks"]) 
            for page in pages
        )
        pages_with_text = sum(1 for page in pages if page["has_text"])
        pages_with_images = sum(1 for page in pages if page["has_images"])
        total_images = sum(len(page["images"]) for page in pages)
        unique_docs = len(set(page["doc_name"] for page in pages))
        
        return {
            "total_pages": len(pages),
            "total_chunks": total_chunks,
            "total_words": total_words,
            "total_tokens": total_tokens,
            "pages_with_text": pages_with_text,
            "pages_with_images": pages_with_images,
            "total_images": total_images,
            "documents_processed": unique_docs,
            "avg_chunk_size": round(total_words / total_chunks, 2) if total_chunks > 0 else 0,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "ocr_enabled": self.enable_ocr,
            "image_extraction_enabled": self.enable_image_extraction
        } 