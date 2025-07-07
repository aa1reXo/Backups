#!/usr/bin/env python3
"""
RAG Service for ChromaDB Operations
Handles vector database operations for the multimodal RAG system
"""

import os
import uuid
from typing import List, Dict, Any, Optional
from loguru import logger

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
except ImportError as e:
    logger.warning(f"ChromaDB or SentenceTransformers not available: {e}")
    chromadb = None
    SentenceTransformer = None

class RAGService:
    """Service for managing ChromaDB operations"""
    
    def __init__(self, persist_directory: str = "./data"):
        """Initialize RAG service with ChromaDB"""
        self.persist_directory = persist_directory
        self.client = None
        self.embedding_model = None
        self.collections = {}
        
        # Create persist directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        self._initialize_chromadb()
        self._load_embedding_model()
    
    def _initialize_chromadb(self):
        """Initialize ChromaDB client"""
        try:
            if chromadb is None:
                logger.error("ChromaDB not available")
                return
            
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info(f"ChromaDB initialized with persist directory: {self.persist_directory}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.client = None
    
    def _load_embedding_model(self):
        """Load sentence transformer model"""
        try:
            if SentenceTransformer is None:
                logger.error("SentenceTransformers not available")
                return
            
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            self.embedding_model = SentenceTransformer(model_name)
            logger.info(f"Loaded embedding model: {model_name}")
            
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.embedding_model = None
    
    def get_or_create_collection(self, collection_name: str = "default"):
        """Get or create a collection"""
        if not self.client:
            logger.error("ChromaDB client not initialized")
            return None
        
        try:
            # Check if collection exists
            try:
                collection = self.client.get_collection(collection_name)
                logger.info(f"Using existing collection: {collection_name}")
            except:
                # Create new collection
                collection = self.client.create_collection(
                    name=collection_name,
                    metadata={"description": f"Collection for {collection_name}"}
                )
                logger.info(f"Created new collection: {collection_name}")
            
            self.collections[collection_name] = collection
            return collection
            
        except Exception as e:
            logger.error(f"Error getting/creating collection {collection_name}: {e}")
            return None
    
    def get_collection(self, collection_name: str = "default"):
        """Get a collection by name"""
        if not self.client:
            return None
        
        try:
            return self.client.get_collection(collection_name)
        except:
            return None
    
    def add_documents(self, documents: List[str], metadatas: List[Dict], 
                     ids: List[str], collection_name: str = "default"):
        """Add documents to a collection"""
        if not self.client or not self.embedding_model:
            logger.error("ChromaDB client or embedding model not available")
            return False
        
        try:
            collection = self.get_or_create_collection(collection_name)
            if not collection:
                return False
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(documents).tolist()
            
            # Add to collection
            collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} documents to collection {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to collection {collection_name}: {e}")
            return False
    
    def query_collection(self, query: str, collection_name: str = "default", 
                        n_results: int = 5) -> Dict[str, Any]:
        """Query a collection"""
        if not self.client or not self.embedding_model:
            logger.error("ChromaDB client or embedding model not available")
            return {"documents": [], "metadatas": [], "distances": []}
        
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                logger.warning(f"Collection {collection_name} not found")
                return {"documents": [], "metadatas": [], "distances": []}
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()
            
            # Query collection
            results = collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            logger.info(f"Query returned {len(results.get('documents', [[]])[0])} results")
            return results
            
        except Exception as e:
            logger.error(f"Error querying collection {collection_name}: {e}")
            return {"documents": [], "metadatas": [], "distances": []}
    
    def list_collections(self) -> List[str]:
        """List all collections"""
        if not self.client:
            return []
        
        try:
            collections = self.client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []
    
    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection"""
        if not self.client:
            return False
        
        try:
            self.client.delete_collection(collection_name)
            logger.info(f"Deleted collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection {collection_name}: {e}")
            return False
    
    def get_collection_stats(self, collection_name: str = "default") -> Dict[str, Any]:
        """Get statistics for a collection"""
        try:
            collection = self.get_collection(collection_name)
            if collection:
                count = collection.count()
                return {
                    "exists": True,
                    "document_count": count,
                    "name": collection_name
                }
            else:
                return {"exists": False, "document_count": 0, "name": collection_name}
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"exists": False, "document_count": 0, "name": collection_name, "error": str(e)} 