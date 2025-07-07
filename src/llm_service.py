#!/usr/bin/env python3
"""
LLM Service for Google Gemini API
Handles language model interactions for the multimodal RAG system
"""

import os
from typing import Optional, Dict, Any
from loguru import logger

try:
    import google.generativeai as genai
except ImportError as e:
    logger.warning(f"Google Generative AI not available: {e}")
    genai = None

class LLMService:
    """Service for managing Google Gemini LLM interactions"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize LLM service with Google Gemini"""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = None
        self.initialized = False
        
        if not self.api_key:
            logger.warning("No Google API key provided. LLM functionality will be limited.")
            return
        
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Google Gemini API"""
        try:
            if genai is None:
                logger.error("Google Generative AI not available")
                return
            
            # Configure the API
            genai.configure(api_key=self.api_key)
            
            # Initialize the model
            self.model = genai.GenerativeModel('gemini-pro')
            self.initialized = True
            
            logger.info("Google Gemini Pro initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Gemini: {e}")
            self.initialized = False
    
    def generate_response(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate response using Google Gemini"""
        if not self.initialized or not self.model:
            logger.error("LLM service not initialized")
            return "I'm sorry, but I'm currently unable to generate responses. Please check the LLM service configuration."
        
        try:
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7,
                    top_p=0.8,
                    top_k=40
                )
            )
            
            if response.text:
                return response.text
            else:
                logger.warning("Empty response from Gemini")
                return "I couldn't generate a response for your query."
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    def generate_response_with_context(self, context: str, question: str, 
                                    max_tokens: int = 1000) -> str:
        """Generate response with specific context"""
        prompt = f"""You are a helpful assistant that answers questions based on the provided context from a PDF document.

Context from the document:
{context}

Question: {question}

Please provide a comprehensive answer based on the context above. If the context doesn't contain enough information to answer the question, please say so. Be concise but thorough in your response."""

        return self.generate_response(prompt, max_tokens)
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the LLM service connection"""
        if not self.initialized:
            return {
                "status": "error",
                "message": "LLM service not initialized",
                "initialized": False
            }
        
        try:
            # Simple test prompt
            test_prompt = "Hello, this is a test. Please respond with 'Test successful' if you can see this message."
            response = self.generate_response(test_prompt, max_tokens=50)
            
            return {
                "status": "success",
                "message": "LLM service is working",
                "initialized": True,
                "test_response": response
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"LLM service test failed: {str(e)}",
                "initialized": False
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the LLM model"""
        return {
            "model_name": "gemini-pro",
            "provider": "Google",
            "initialized": self.initialized,
            "api_key_configured": bool(self.api_key)
        } 