import os
import time
import requests
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger
import google.generativeai as genai
from .utils import log_vector_search, log_llm_call, count_tokens
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class RAGSystem:
    def __init__(self, vector_db_path: str = "/app/data/chromadb"):
        """
        Initialize RAG system with simple text-based storage
        
        Args:
            vector_db_path: Path to ChromaDB storage (not used in this simplified version)
        """
        self.vector_db_path = vector_db_path
        self.documents = []
        self.metadatas = []
        
        # Google Gemini API configuration
        self.gemini_api_key = os.getenv("GOOGLE_API_KEY", "")
        self.gemini_model = "gemini-1.5-flash"  # Fast and efficient model
        
        # Initialize components
        self._initialize_gemini()
        
    def _initialize_gemini(self):
        """Initialize Google Gemini"""
        try:
            if self.gemini_api_key:
                genai.configure(api_key=self.gemini_api_key)
                logger.info("Google Gemini initialized successfully")
            else:
                logger.warning("GOOGLE_API_KEY not set. LLM functionality will be limited.")
        except Exception as e:
            logger.error(f"Error initializing Gemini: {e}")
    
    def add_chunks_to_vector_db(self, chunks: List[Dict[str, Any]]) -> bool:
        """Add processed chunks to simple storage"""
        if not chunks:
            logger.warning("No chunks to add to storage")
            return False
        
        try:
            # Store in memory (simplified version)
            self.documents.extend([chunk["text"] for chunk in chunks])
            self.metadatas.extend([{
                "doc_name": chunk["doc_name"],
                "chunk_index": chunk["chunk_index"],
                "word_count": chunk["word_count"],
                "token_count": chunk["token_count"]
            } for chunk in chunks])
            
            logger.info(f"Successfully added {len(chunks)} chunks to storage")
            return True
            
        except Exception as e:
            logger.error(f"Error adding chunks to storage: {e}")
            return False
    
    def get_context(self, question: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for a question using simple text matching
        
        Args:
            question: User question
            top_k: Number of top results to return
            
        Returns:
            List of relevant chunks with scores
        """
        start_time = time.time()
        
        try:
            if not self.documents:
                return []
            
            # Simple text-based relevance scoring
            question_words = set(question.lower().split())
            context_chunks = []
            
            for idx, doc in enumerate(self.documents):
                doc_words = set(doc.lower().split())
                # Calculate simple word overlap
                overlap = len(question_words.intersection(doc_words))
                relevance_score = overlap / max(len(question_words), 1)
                
                chunk = {
                    "chunk_id": f"chunk_{idx}",
                    "text": doc,
                    "doc_name": self.metadatas[idx]["doc_name"],
                    "chunk_index": self.metadatas[idx]["chunk_index"],
                    "relevance_score": relevance_score,
                    "word_count": self.metadatas[idx]["word_count"],
                    "token_count": self.metadatas[idx]["token_count"]
                }
                context_chunks.append(chunk)
            
            # Sort by relevance and take top_k
            context_chunks.sort(key=lambda x: x["relevance_score"], reverse=True)
            context_chunks = context_chunks[:top_k]
            
            search_time = time.time() - start_time
            log_vector_search(question, top_k, search_time, len(context_chunks))
            
            return context_chunks
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []
    
    def _call_gemini_llm(self, prompt: str) -> Tuple[str, int]:
        """Call Google Gemini model"""
        if not self.gemini_api_key:
            logger.error("Gemini API key not configured")
            return "Error: LLM service not configured. Please set GOOGLE_API_KEY environment variable.", 0
        
        try:
            # Initialize the model
            model = genai.GenerativeModel(self.gemini_model)
            
            # Generate response
            response = model.generate_content(prompt)
            
            # Get response text
            content = response.text
            
            # Estimate token count (Gemini doesn't provide exact token count in response)
            token_count = count_tokens(prompt) + count_tokens(content)
            
            return content, token_count
                
        except Exception as e:
            logger.error(f"Error calling Gemini LLM: {e}")
            return f"Error: {str(e)}", 0
    
    def _create_prompt_template(self, question: str, context_chunks: List[Dict[str, Any]]) -> str:
        """Create prompt template for LLM"""
        if not context_chunks:
            return f"Question: {question}\n\nAnswer: I don't have enough information to answer this question."
        
        context_text = "\n\n".join([
            f"Document: {chunk['doc_name']} (Chunk {chunk['chunk_index']})\n"
            f"Relevance Score: {chunk['relevance_score']:.3f}\n"
            f"Content: {chunk['text']}"
            for chunk in context_chunks
        ])
        
        prompt = f"""Based on the following context from Qualcomm Linux PDF manuals, provide a concise and accurate answer to the question.

Context:
{context_text}

Question: {question}

Instructions:
1. Answer the question based only on the provided context
2. Be concise and technical
3. If the context doesn't contain enough information, say so
4. Include relevant technical details and specifications
5. Cite the source documents when possible

Answer:"""
        
        return prompt
    
    def answer_question(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Answer a question using RAG
        
        Args:
            question: User question
            top_k: Number of context chunks to retrieve
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        start_time = time.time()
        
        try:
            # Get relevant context
            context_chunks = self.get_context(question, top_k)
            
            if not context_chunks:
                return {
                    "answer": "I couldn't find relevant information in the Qualcomm Linux manuals to answer your question.",
                    "sources": [],
                    "context_chunks": [],
                    "total_tokens": 0,
                    "vector_search_time": 0,
                    "llm_time": 0,
                    "total_time": time.time() - start_time
                }
            
            # Create prompt
            prompt = self._create_prompt_template(question, context_chunks)
            
            # Call LLM
            llm_start_time = time.time()
            answer, token_count = self._call_gemini_llm(prompt)
            llm_time = time.time() - llm_start_time
            
            log_llm_call(prompt, answer, llm_time, token_count)
            
            # Prepare sources
            sources = [
                {
                    "doc_name": chunk["doc_name"],
                    "chunk_index": chunk["chunk_index"],
                    "relevance_score": chunk["relevance_score"]
                }
                for chunk in context_chunks
            ]
            
            total_time = time.time() - start_time
            
            return {
                "answer": answer,
                "sources": sources,
                "context_chunks": context_chunks,
                "total_tokens": token_count,
                "vector_search_time": llm_start_time - start_time,
                "llm_time": llm_time,
                "total_time": total_time
            }
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                "answer": f"Error processing your question: {str(e)}",
                "sources": [],
                "context_chunks": [],
                "total_tokens": 0,
                "vector_search_time": 0,
                "llm_time": 0,
                "total_time": time.time() - start_time
            }
    
    def get_vector_db_stats(self) -> Dict[str, Any]:
        """Get vector database statistics"""
        try:
            return {
                "total_chunks": len(self.documents),
                "collection_name": "simple_storage",
                "embedding_model": "text_based_matching"
            }
        except Exception as e:
            logger.error(f"Error getting vector DB stats: {e}")
            return {"total_chunks": 0, "error": str(e)}
    
    def clear_vector_db(self) -> bool:
        """Clear all data from vector database"""
        try:
            self.documents = []
            self.metadatas = []
            logger.info("Simple storage cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Error clearing storage: {e}")
            return False 