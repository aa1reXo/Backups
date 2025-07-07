import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import time
from loguru import logger

from .rag_system import RAGSystem
from .pdf_processor import PDFProcessor
from .utils import setup_logging

# Setup logging
setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title="Qualcomm Linux RAG Q&A Service",
    description="A RAG-based Q&A service for Qualcomm Linux documentation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize RAG system
rag_system = RAGSystem()

# Initialize PDF processor
pdf_processor = PDFProcessor()

# API Key validation
def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key"""
    api_key = credentials.credentials
    expected_key = os.getenv("API_KEY", "test_api_key")
    
    if api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return api_key

# Pydantic models
class QueryRequest(BaseModel):
    question: str
    max_results: int = 5
    include_sources: bool = True

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    context_chunks: List[Dict[str, Any]]
    total_tokens: int
    vector_search_time: float
    llm_time: float
    total_time: float

class ProcessPDFRequest(BaseModel):
    filename: str

class ProcessPDFResponse(BaseModel):
    success: bool
    message: str
    chunks_processed: int
    processing_time: float

class StatsResponse(BaseModel):
    vector_db_stats: Dict[str, Any]
    llm_status: str
    total_requests: int
    average_response_time: float

# Global stats
request_count = 0
total_response_time = 0.0

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Qualcomm Linux RAG Q&A Service",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/query", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    api_key: str = Depends(verify_api_key)
):
    """Query the RAG system with a question"""
    global request_count, total_response_time
    
    start_time = time.time()
    
    try:
        # Get answer from RAG system
        result = rag_system.answer_question(
            request.question,
            top_k=request.max_results
        )
        
        # Update stats
        request_count += 1
        total_response_time += result["total_time"]
        
        # Filter sources if requested
        if not request.include_sources:
            result["sources"] = []
            result["context_chunks"] = []
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )

@app.post("/process-pdf", response_model=ProcessPDFResponse)
async def process_pdf(
    request: ProcessPDFRequest,
    api_key: str = Depends(verify_api_key)
):
    """Process a PDF file and add to vector database"""
    try:
        start_time = time.time()
        
        # Process PDF
        chunks = pdf_processor.process_pdf(request.filename)
        
        if not chunks:
            return ProcessPDFResponse(
                success=False,
                message="No chunks extracted from PDF",
                chunks_processed=0,
                processing_time=time.time() - start_time
            )
        
        # Add to vector database
        success = rag_system.add_chunks_to_vector_db(chunks)
        
        processing_time = time.time() - start_time
        
        if success:
            return ProcessPDFResponse(
                success=True,
                message=f"Successfully processed {len(chunks)} chunks",
                chunks_processed=len(chunks),
                processing_time=processing_time
            )
        else:
            return ProcessPDFResponse(
                success=False,
                message="Failed to add chunks to vector database",
                chunks_processed=len(chunks),
                processing_time=processing_time
            )
            
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing PDF: {str(e)}"
        )

@app.get("/stats", response_model=StatsResponse)
async def get_stats(api_key: str = Depends(verify_api_key)):
    """Get system statistics"""
    try:
        vector_db_stats = rag_system.get_vector_db_stats()
        
        # Check LLM status
        llm_status = "available" if os.getenv("GEMINI_API_KEY") else "not_configured"
        
        # Calculate average response time
        avg_response_time = total_response_time / request_count if request_count > 0 else 0.0
        
        return StatsResponse(
            vector_db_stats=vector_db_stats,
            llm_status=llm_status,
            total_requests=request_count,
            average_response_time=avg_response_time
        )
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting stats: {str(e)}"
        )

@app.delete("/clear-db")
async def clear_database(api_key: str = Depends(verify_api_key)):
    """Clear the vector database"""
    try:
        success = rag_system.clear_vector_db()
        
        if success:
            return {"message": "Vector database cleared successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to clear vector database"
            )
            
    except Exception as e:
        logger.error(f"Error clearing database: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing database: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 