#!/usr/bin/env python3
"""
Integration Example: Multimodal PDF Processor with RAG System
Shows how to use the new multimodal processor with existing ChromaDB and Gemini
"""

import os
import sys
from pathlib import Path
import json

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.multimodal_pdf_processor import MultimodalPDFProcessor
from src.rag_service import RAGService
from src.llm_service import LLMService
from loguru import logger

class MultimodalRAGService:
    """Enhanced RAG service with multimodal PDF processing"""
    
    def __init__(self, 
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200,
                 ocr_lang: str = 'eng',
                 dpi: int = 300):
        """
        Initialize multimodal RAG service
        
        Args:
            chunk_size: Target words per chunk
            chunk_overlap: Overlapping words between chunks
            ocr_lang: OCR language
            dpi: Image resolution for extraction
        """
        # Initialize multimodal PDF processor
        self.pdf_processor = MultimodalPDFProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            ocr_lang=ocr_lang,
            dpi=dpi,
            enable_ocr=True,
            enable_image_extraction=True
        )
        
        # Initialize RAG service
        self.rag_service = RAGService()
        
        # Initialize LLM service
        self.llm_service = LLMService()
        
        logger.info("Multimodal RAG Service initialized")
    
    def process_and_ingest_pdf(self, pdf_path: str, collection_name: str = None) -> dict:
        """
        Process PDF and ingest into vector database
        
        Args:
            pdf_path: Path to PDF file
            collection_name: Name for ChromaDB collection
            
        Returns:
            dict: Processing statistics and results
        """
        logger.info(f"Processing and ingesting PDF: {pdf_path}")
        
        # Process PDF with multimodal processor
        pages = self.pdf_processor.process_pdf_file(pdf_path)
        
        if not pages:
            logger.error("No pages processed from PDF")
            return {"error": "No pages processed"}
        
        # Get processing statistics
        stats = self.pdf_processor.get_processing_stats(pages)
        
        # Prepare documents for ingestion
        documents = []
        metadatas = []
        ids = []
        
        for page in pages:
            # Add text chunks
            for chunk in page["text_chunks"]:
                documents.append(chunk["text"])
                metadatas.append({
                    "doc_name": chunk["doc_name"],
                    "page_num": chunk["page_num"],
                    "chunk_index": chunk["chunk_index"],
                    "word_count": chunk["word_count"],
                    "token_count": chunk["token_count"],
                    "content_type": "text",
                    "has_images": page["has_images"],
                    "image_count": len(page["images"])
                })
                ids.append(chunk["chunk_id"])
            
            # Add page image as separate document (if available)
            if page.get("page_image"):
                documents.append(f"[PAGE_IMAGE] Page {page['page_num']} of {page['doc_name']}")
                metadatas.append({
                    "doc_name": page["doc_name"],
                    "page_num": page["page_num"],
                    "content_type": "page_image",
                    "has_text": page["has_text"],
                    "has_images": page["has_images"],
                    "image_count": len(page["images"])
                })
                ids.append(f"{page['doc_name']}_page_{page['page_num']}_image")
        
        # Ingest into vector database
        if documents:
            collection_name = collection_name or f"multimodal_{os.path.basename(pdf_path).replace('.pdf', '')}"
            
            try:
                self.rag_service.add_documents(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids,
                    collection_name=collection_name
                )
                
                logger.info(f"Successfully ingested {len(documents)} documents into collection: {collection_name}")
                
                return {
                    "success": True,
                    "collection_name": collection_name,
                    "documents_ingested": len(documents),
                    "pages_processed": len(pages),
                    "processing_stats": stats
                }
                
            except Exception as e:
                logger.error(f"Error ingesting documents: {e}")
                return {"error": str(e)}
        
        return {"error": "No documents to ingest"}
    
    def query_with_context(self, query: str, collection_name: str, top_k: int = 5) -> dict:
        """
        Query the multimodal RAG system
        
        Args:
            query: User query
            collection_name: Collection to search
            top_k: Number of results to return
            
        Returns:
            dict: Query results with context
        """
        logger.info(f"Querying multimodal RAG: {query}")
        
        try:
            # Search for relevant documents
            results = self.rag_service.query_collection(
                query=query,
                collection_name=collection_name,
                n_results=top_k
            )
            
            if not results or not results.get("documents"):
                return {"error": "No results found"}
            
            # Prepare context for LLM
            context_docs = results["documents"][0]  # List of documents
            context_metadatas = results["metadatas"][0]  # List of metadatas
            
            # Build context string
            context_parts = []
            for i, doc in enumerate(context_docs):
                metadata = context_metadatas[i]
                
                if metadata.get("content_type") == "page_image":
                    context_parts.append(f"[Page Image] {doc}")
                else:
                    context_parts.append(f"[Page {metadata.get('page_num', 'N/A')}] {doc}")
            
            context = "\n\n".join(context_parts)
            
            # Generate response using LLM
            prompt = f"""You are a helpful assistant that answers questions based on the provided context from a PDF document.

Context from the document:
{context}

Question: {query}

Please provide a comprehensive answer based on the context above. If the context doesn't contain enough information to answer the question, please say so."""

            response = self.llm_service.generate_response(prompt)
            
            return {
                "query": query,
                "response": response,
                "context_documents": len(context_docs),
                "collection_name": collection_name,
                "context_preview": context[:500] + "..." if len(context) > 500 else context
            }
            
        except Exception as e:
            logger.error(f"Error querying RAG system: {e}")
            return {"error": str(e)}
    
    def get_collection_info(self, collection_name: str) -> dict:
        """Get information about a collection"""
        try:
            collection = self.rag_service.get_collection(collection_name)
            if collection:
                count = collection.count()
                return {
                    "collection_name": collection_name,
                    "document_count": count,
                    "exists": True
                }
            else:
                return {"collection_name": collection_name, "exists": False}
        except Exception as e:
            return {"error": str(e)}

def main():
    """Example usage of Multimodal RAG Service"""
    
    # Initialize service
    multimodal_rag = MultimodalRAGService(
        chunk_size=1000,
        chunk_overlap=200,
        ocr_lang='eng',
        dpi=300
    )
    
    # Example PDF path (replace with your PDF)
    pdf_path = "sample.pdf"
    
    if not os.path.exists(pdf_path):
        logger.warning(f"PDF file {pdf_path} not found. Please provide a valid PDF path.")
        return
    
    # Process and ingest PDF
    logger.info("=== Processing and Ingesting PDF ===")
    result = multimodal_rag.process_and_ingest_pdf(pdf_path)
    
    if result.get("success"):
        collection_name = result["collection_name"]
        
        logger.info(f"Successfully processed PDF:")
        logger.info(f"  - Pages processed: {result['pages_processed']}")
        logger.info(f"  - Documents ingested: {result['documents_ingested']}")
        logger.info(f"  - Collection: {collection_name}")
        
        # Example queries
        example_queries = [
            "What is the main topic of this document?",
            "Are there any images or diagrams mentioned?",
            "What are the key points from the first few pages?"
        ]
        
        logger.info("\n=== Example Queries ===")
        for query in example_queries:
            logger.info(f"\nQuery: {query}")
            response = multimodal_rag.query_with_context(query, collection_name)
            
            if response.get("error"):
                logger.error(f"Error: {response['error']}")
            else:
                logger.info(f"Response: {response['response']}")
                logger.info(f"Context documents: {response['context_documents']}")
    
    else:
        logger.error(f"Error processing PDF: {result.get('error')}")

if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    
    main() 