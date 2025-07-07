import os
import re
from typing import List, Dict, Any, Tuple
from PyPDF2 import PdfReader
from loguru import logger
from .utils import count_tokens, create_chunk_id

class PDFProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize PDF processor
        
        Args:
            chunk_size: Target number of words per chunk
            chunk_overlap: Number of overlapping words between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                    
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep technical terms
        text = re.sub(r'[^\w\s\-\.\,\;\:\!\?\(\)\[\]\{\}\+\=\*\&\^\%\$\#\@]', '', text)
        
        # Normalize line breaks
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        return text.strip()
    
    def split_text_into_chunks(self, text: str, doc_name: str) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks"""
        if not text:
            return []
            
        # Clean text
        text = self.clean_text(text)
        words = text.split()
        
        if len(words) <= self.chunk_size:
            return [{
                "chunk_id": create_chunk_id(doc_name, 0),
                "text": text,
                "doc_name": doc_name,
                "chunk_index": 0,
                "word_count": len(words),
                "token_count": count_tokens(text)
            }]
        
        chunks = []
        chunk_index = 0
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            
            if len(chunk_text.strip()) < 50:  # Skip very short chunks
                continue
                
            chunks.append({
                "chunk_id": create_chunk_id(doc_name, chunk_index),
                "text": chunk_text,
                "doc_name": doc_name,
                "chunk_index": chunk_index,
                "word_count": len(chunk_words),
                "token_count": count_tokens(chunk_text)
            })
            
            chunk_index += 1
            
            # Stop if we've covered all words
            if i + self.chunk_size >= len(words):
                break
        
        return chunks
    
    def process_pdf_file(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Process a single PDF file and return chunks"""
        doc_name = os.path.basename(pdf_path).replace('.pdf', '')
        
        logger.info(f"Processing PDF: {pdf_path}")
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            logger.warning(f"No text extracted from {pdf_path}")
            return []
        
        # Split into chunks
        chunks = self.split_text_into_chunks(text, doc_name)
        
        logger.info(f"Created {len(chunks)} chunks from {pdf_path}")
        return chunks
    
    def process_pdf_folder(self, folder_path: str) -> List[Dict[str, Any]]:
        """Process all PDF files in a folder"""
        all_chunks = []
        
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
                chunks = self.process_pdf_file(pdf_path)
                all_chunks.extend(chunks)
            except Exception as e:
                logger.error(f"Error processing {pdf_path}: {e}")
                continue
        
        logger.info(f"Total chunks created: {len(all_chunks)}")
        return all_chunks
    
    def get_processing_stats(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about processed chunks"""
        if not chunks:
            return {
                "total_chunks": 0,
                "total_words": 0,
                "total_tokens": 0,
                "avg_chunk_size": 0,
                "documents_processed": 0
            }
        
        total_words = sum(chunk["word_count"] for chunk in chunks)
        total_tokens = sum(chunk["token_count"] for chunk in chunks)
        unique_docs = len(set(chunk["doc_name"] for chunk in chunks))
        
        return {
            "total_chunks": len(chunks),
            "total_words": total_words,
            "total_tokens": total_tokens,
            "avg_chunk_size": round(total_words / len(chunks), 2),
            "documents_processed": unique_docs,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap
        } 