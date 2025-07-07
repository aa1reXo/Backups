#!/usr/bin/env python3
"""
Main FastAPI Application for Multimodal RAG System
Integrates multimodal PDF processing with ChromaDB and Gemini
"""

import os
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from loguru import logger

# Import our services
from src.multimodal_pdf_processor import MultimodalPDFProcessor
from src.rag_service import RAGService
from src.llm_service import LLMService

# Initialize FastAPI app
app = FastAPI(
    title="Multimodal RAG Q&A Service",
    description="Advanced PDF processing with OCR and multimodal capabilities",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for tracking
start_time = datetime.now()
total_queries = 0
response_times = []

# Initialize services
multimodal_processor = MultimodalPDFProcessor(
    chunk_size=1000,
    chunk_overlap=200,
    ocr_lang='eng',
    dpi=300,
    enable_ocr=True,
    enable_image_extraction=True
)

rag_service = RAGService()
llm_service = LLMService()

# Pydantic models for API requests/responses
class HealthResponse(BaseModel):
    status: str
    timestamp: str

class InfoResponse(BaseModel):
    team_name: str
    model_info: str
    docs_count: int
    total_chunks: int
    vector_db: str
    embedding_model: str
    chunk_size: int
    chunk_overlap: int
    timestamp: str

class StatsResponse(BaseModel):
    total_queries: int
    avg_response_time_ms: float
    uptime_seconds: int

class CreateRequest(BaseModel):
    folder_path: str = Field(..., description="Path to folder containing PDFs")

class CreateResponse(BaseModel):
    success: bool
    message: str
    collection_name: Optional[str] = None
    documents_processed: Optional[int] = None
    pages_processed: Optional[int] = None
    processing_stats: Optional[Dict[str, Any]] = None

class ContextRequest(BaseModel):
    question: str = Field(..., description="Question to search for context")

class ContextResponse(BaseModel):
    question: str
    context: List[str]
    sources: List[Dict[str, Any]]
    total_results: int

class QueryRequest(BaseModel):
    question: str = Field(..., description="Question to ask")
    max_results: int = Field(default=5, description="Maximum number of results to return")
    include_sources: bool = Field(default=True, description="Whether to include sources in response")

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[Dict[str, Any]]
    context_documents: int
    response_time_ms: float
    processing_stats: Dict[str, Any]

# Utility functions
def get_uptime_seconds() -> int:
    """Get uptime in seconds"""
    return int((datetime.now() - start_time).total_seconds())

def get_avg_response_time() -> float:
    """Get average response time in milliseconds"""
    if not response_times:
        return 0.0
    return sum(response_times) / len(response_times)

def track_response_time(response_time_ms: float):
    """Track response time for statistics"""
    global total_queries
    total_queries += 1
    response_times.append(response_time_ms)
    
    # Keep only last 1000 response times to prevent memory issues
    if len(response_times) > 1000:
        response_times.pop(0)

def get_collection_stats(collection_name: str) -> Dict[str, Any]:
    """Get statistics for a collection"""
    try:
        collection = rag_service.get_collection(collection_name)
        if collection:
            return {
                "exists": True,
                "document_count": collection.count(),
                "name": collection_name
            }
        else:
            return {"exists": False, "document_count": 0, "name": collection_name}
    except Exception as e:
        logger.error(f"Error getting collection stats: {e}")
        return {"exists": False, "document_count": 0, "name": collection_name, "error": str(e)}

# API Endpoints

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat()
    )

@app.get("/info", response_model=InfoResponse)
async def get_info():
    """Get system information"""
    # Get default collection stats
    default_collection = "default"
    collection_stats = get_collection_stats(default_collection)
    
    return InfoResponse(
        team_name="Qualcomm Linux RAG Team",
        model_info="Google Gemini Pro + Multimodal PDF Processing",
        docs_count=collection_stats.get("document_count", 0),
        total_chunks=collection_stats.get("document_count", 0),  # Each document is a chunk
        vector_db="ChromaDB",
        embedding_model="sentence-transformers/all-MiniLM-L6-v2",
        chunk_size=multimodal_processor.chunk_size,
        chunk_overlap=multimodal_processor.chunk_overlap,
        timestamp=datetime.now().isoformat()
    )

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get system statistics"""
    return StatsResponse(
        total_queries=total_queries,
        avg_response_time_ms=get_avg_response_time(),
        uptime_seconds=get_uptime_seconds()
    )

@app.post("/create", response_model=CreateResponse)
async def create_vector_db(request: CreateRequest):
    """Create vector database from PDF folder"""
    start_time = time.time()
    
    try:
        folder_path = request.folder_path
        
        # Validate folder path
        if not os.path.exists(folder_path):
            raise HTTPException(status_code=404, detail=f"Folder not found: {folder_path}")
        
        # Check if folder contains PDFs
        pdf_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
        
        if not pdf_files:
            raise HTTPException(status_code=400, detail="No PDF files found in the specified folder")
        
        logger.info(f"Processing {len(pdf_files)} PDF files from {folder_path}")
        
        # Process all PDFs
        all_pages = []
        for pdf_path in pdf_files:
            try:
                pages = multimodal_processor.process_pdf_file(pdf_path)
                all_pages.extend(pages)
                logger.info(f"Processed {len(pages)} pages from {pdf_path}")
            except Exception as e:
                logger.error(f"Error processing {pdf_path}: {e}")
                continue
        
        if not all_pages:
            raise HTTPException(status_code=500, detail="No pages processed from any PDF files")
        
        # Get processing statistics
        stats = multimodal_processor.get_processing_stats(all_pages)
        
        # Prepare documents for ingestion
        documents = []
        metadatas = []
        ids = []
        
        for page in all_pages:
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
        
        # Create collection name from folder
        collection_name = f"multimodal_{os.path.basename(folder_path)}"
        
        # Ingest into vector database
        rag_service.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            collection_name=collection_name
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        logger.info(f"Successfully created vector database:")
        logger.info(f"  - Collection: {collection_name}")
        logger.info(f"  - Documents ingested: {len(documents)}")
        logger.info(f"  - Pages processed: {len(all_pages)}")
        logger.info(f"  - Processing time: {processing_time:.2f}ms")
        
        return CreateResponse(
            success=True,
            message=f"Successfully processed {len(all_pages)} pages and ingested {len(documents)} documents",
            collection_name=collection_name,
            documents_processed=len(documents),
            pages_processed=len(all_pages),
            processing_stats=stats
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating vector database: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/context", response_model=ContextResponse)
async def get_context(request: ContextRequest):
    """Get context for a question without generating answer"""
    start_time = time.time()
    
    try:
        # Search for relevant documents
        results = rag_service.query_collection(
            query=request.question,
            collection_name="default",
            n_results=5
        )
        
        if not results or not results.get("documents"):
            return ContextResponse(
                question=request.question,
                context=[],
                sources=[],
                total_results=0
            )
        
        # Prepare context and sources
        context_docs = results["documents"][0]
        context_metadatas = results["metadatas"][0]
        context_distances = results["distances"][0]
        
        sources = []
        for i, metadata in enumerate(context_metadatas):
            sources.append({
                "doc_name": metadata.get("doc_name", "Unknown"),
                "page_num": metadata.get("page_num", "N/A"),
                "chunk_index": metadata.get("chunk_index", "N/A"),
                "content_type": metadata.get("content_type", "text"),
                "similarity_score": 1 - context_distances[i] if context_distances else 0,
                "word_count": metadata.get("word_count", 0),
                "has_images": metadata.get("has_images", False)
            })
        
        response_time = (time.time() - start_time) * 1000
        track_response_time(response_time)
        
        return ContextResponse(
            question=request.question,
            context=context_docs,
            sources=sources,
            total_results=len(context_docs)
        )
        
    except Exception as e:
        logger.error(f"Error getting context: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving context: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """Query the RAG system with question and get answer"""
    start_time = time.time()
    
    try:
        # Search for relevant documents
        results = rag_service.query_collection(
            query=request.question,
            collection_name="default",
            n_results=request.max_results
        )
        
        if not results or not results.get("documents"):
            return QueryResponse(
                question=request.question,
                answer="I couldn't find any relevant information to answer your question.",
                sources=[],
                context_documents=0,
                response_time_ms=(time.time() - start_time) * 1000,
                processing_stats={"error": "No results found"}
            )
        
        # Prepare context for LLM
        context_docs = results["documents"][0]
        context_metadatas = results["metadatas"][0]
        context_distances = results["distances"][0]
        
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

Question: {request.question}

Please provide a comprehensive answer based on the context above. If the context doesn't contain enough information to answer the question, please say so."""

        answer = llm_service.generate_response(prompt)
        
        # Prepare sources if requested
        sources = []
        if request.include_sources:
            for i, metadata in enumerate(context_metadatas):
                sources.append({
                    "doc_name": metadata.get("doc_name", "Unknown"),
                    "page_num": metadata.get("page_num", "N/A"),
                    "chunk_index": metadata.get("chunk_index", "N/A"),
                    "content_type": metadata.get("content_type", "text"),
                    "similarity_score": 1 - context_distances[i] if context_distances else 0,
                    "word_count": metadata.get("word_count", 0),
                    "has_images": metadata.get("has_images", False)
                })
        
        response_time = (time.time() - start_time) * 1000
        track_response_time(response_time)
        
        return QueryResponse(
            question=request.question,
            answer=answer,
            sources=sources,
            context_documents=len(context_docs),
            response_time_ms=response_time,
            processing_stats={
                "total_chunks_processed": len(context_docs),
                "avg_similarity_score": sum(1 - d for d in context_distances) / len(context_distances) if context_distances else 0,
                "has_images": any(m.get("has_images", False) for m in context_metadatas)
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

# Additional utility endpoints

@app.get("/collections")
async def list_collections():
    """List all available collections"""
    try:
        collections = rag_service.list_collections()
        return {
            "collections": collections,
            "total_collections": len(collections)
        }
    except Exception as e:
        logger.error(f"Error listing collections: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing collections: {str(e)}")

@app.get("/collections/{collection_name}")
async def get_collection_info(collection_name: str):
    """Get information about a specific collection"""
    try:
        stats = get_collection_stats(collection_name)
        return stats
    except Exception as e:
        logger.error(f"Error getting collection info: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting collection info: {str(e)}")

@app.delete("/collections/{collection_name}")
async def delete_collection(collection_name: str):
    """Delete a collection"""
    try:
        success = rag_service.delete_collection(collection_name)
        if success:
            return {"success": True, "message": f"Collection '{collection_name}' deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found")
    except Exception as e:
        logger.error(f"Error deleting collection: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting collection: {str(e)}")

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Multimodal RAG Q&A Service...")
    logger.info(f"OCR enabled: {multimodal_processor.enable_ocr}")
    logger.info(f"Image extraction enabled: {multimodal_processor.enable_image_extraction}")
    logger.info(f"Chunk size: {multimodal_processor.chunk_size}")
    logger.info(f"Chunk overlap: {multimodal_processor.chunk_overlap}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Multimodal RAG Q&A Service...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 