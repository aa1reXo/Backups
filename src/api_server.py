import os
import time
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger

from .pdf_processor import PDFProcessor
from .rag_system import RAGSystem
from .utils import setup_logging, log_request, get_metrics, validate_api_key, format_timestamp

# Initialize FastAPI app
app = FastAPI(
    title="Qualcomm Linux RAG Q&A Service",
    description="Retrieval-Augmented Generation service for Qualcomm Linux PDF manuals",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Security
security = HTTPBearer()

# Global instances
pdf_processor = None
rag_system = None

# Request/Response models
class CreateRequest(BaseModel):
    folder_path: str

class ContextRequest(BaseModel):
    question: str
    max_results: Optional[int] = 5

class QueryRequest(BaseModel):
    question: str
    max_results: Optional[int] = 5
    include_sources: Optional[bool] = True

class ContextResponse(BaseModel):
    question: str
    context_chunks: list
    total_chunks: int
    timestamp: str

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list
    total_tokens: int
    vector_search_time: float
    llm_time: float
    total_time: float
    timestamp: str

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
    uptime_seconds: float

# Dependency for API key validation
async def verify_api_key(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="API key required")
    
    # Extract API key from Bearer token
    try:
        api_key = authorization.replace("Bearer ", "")
    except:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    if not validate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return api_key

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global pdf_processor, rag_system
    
    # Setup logging
    setup_logging()
    logger.info("Starting Qualcomm Linux RAG Q&A Service")
    
    try:
        # Initialize PDF processor
        pdf_processor = PDFProcessor(chunk_size=1000, chunk_overlap=200)
        logger.info("PDF processor initialized")
        
        # Initialize RAG system
        rag_system = RAGSystem()
        logger.info("RAG system initialized")
        
        logger.info("Service startup completed successfully")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": format_timestamp()
    }

@app.get("/info", response_model=InfoResponse, dependencies=[Depends(verify_api_key)])
async def get_info():
    """Get service information"""
    try:
        vector_stats = rag_system.get_vector_db_stats()
        
        return {
            "team_name": "Hkthon",
            "model_info": "qGenie llama3.1:70b",
            "docs_count": vector_stats.get("total_chunks", 0),  # Simplified for now
            "total_chunks": vector_stats.get("total_chunks", 0),
            "vector_db": "ChromaDB",
            "embedding_model": "stella_en_400M_v5",
            "chunk_size": pdf_processor.chunk_size,
            "chunk_overlap": pdf_processor.chunk_overlap,
            "timestamp": format_timestamp()
        }
    except Exception as e:
        logger.error(f"Error getting info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats", response_model=StatsResponse, dependencies=[Depends(verify_api_key)])
async def get_stats():
    """Get service statistics"""
    try:
        metrics = get_metrics()
        return {
            "total_queries": metrics["total_queries"],
            "avg_response_time_ms": metrics["avg_response_time_ms"],
            "uptime_seconds": metrics["uptime_seconds"]
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create", dependencies=[Depends(verify_api_key)])
async def create_vector_db(request: CreateRequest):
    """Create vector database from PDF folder"""
    start_time = time.time()
    
    try:
        logger.info(f"Creating vector DB from folder: {request.folder_path}")
        
        # Process PDFs
        chunks = pdf_processor.process_pdf_folder(request.folder_path)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No PDF files found or processed")
        
        # Clear existing vector DB
        rag_system.clear_vector_db()
        
        # Add chunks to vector DB
        success = rag_system.add_chunks_to_vector_db(chunks)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to create vector database")
        
        # Get processing stats
        stats = pdf_processor.get_processing_stats(chunks)
        
        response_time = time.time() - start_time
        log_request("/create", {"folder_path": request.folder_path}, response_time)
        
        return {
            "status": "success",
            "message": f"Vector database created successfully",
            "stats": stats,
            "processing_time": response_time,
            "timestamp": format_timestamp()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating vector DB: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/context", response_model=ContextResponse, dependencies=[Depends(verify_api_key)])
async def get_context(request: ContextRequest):
    """Get relevant context for a question"""
    start_time = time.time()
    
    try:
        context_chunks = rag_system.get_context(request.question, request.max_results)
        
        response_time = time.time() - start_time
        log_request("/context", {"question": request.question, "max_results": request.max_results}, response_time)
        
        return {
            "question": request.question,
            "context_chunks": context_chunks,
            "total_chunks": len(context_chunks),
            "timestamp": format_timestamp()
        }
        
    except Exception as e:
        logger.error(f"Error getting context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse, dependencies=[Depends(verify_api_key)])
async def query_rag(request: QueryRequest):
    """Query the RAG system for an answer"""
    start_time = time.time()
    
    try:
        # Get answer from RAG system
        result = rag_system.answer_question(request.question, request.max_results)
        
        response_time = time.time() - start_time
        log_request("/query", {"question": request.question, "max_results": request.max_results}, response_time)
        
        # Prepare response
        response = {
            "question": request.question,
            "answer": result["answer"],
            "sources": result["sources"] if request.include_sources else [],
            "total_tokens": result["total_tokens"],
            "vector_search_time": result["vector_search_time"],
            "llm_time": result["llm_time"],
            "total_time": result["total_time"],
            "timestamp": format_timestamp()
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return {"error": "Internal server error", "detail": str(exc)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 