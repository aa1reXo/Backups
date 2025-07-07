import os
import time
import json
from datetime import datetime
from typing import Dict, Any, Optional
from loguru import logger

# Try to import tiktoken, fallback to simple token counting
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logger.warning("tiktoken not available, using simple token counting")

# Global metrics
_metrics = {
    "total_queries": 0,
    "total_response_time": 0,
    "start_time": time.time(),
    "vector_search_times": [],
    "llm_times": [],
    "token_usage": []
}

def setup_logging():
    """Setup structured logging"""
    logger.remove()
    logger.add(
        "logs/rag_service.log",
        rotation="10 MB",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="INFO"
    )
    logger.add(
        lambda msg: print(msg, end=""),
        format="{time:HH:mm:ss} | {level} | {message}",
        level="INFO"
    )

def log_request(endpoint: str, request_data: Dict[str, Any], response_time: float):
    """Log API request details"""
    _metrics["total_queries"] += 1
    _metrics["total_response_time"] += response_time
    
    logger.info(f"API Request | {endpoint} | {response_time:.3f}s | {request_data}")

def log_vector_search(query: str, top_k: int, search_time: float, results_count: int):
    """Log vector search performance"""
    _metrics["vector_search_times"].append(search_time)
    logger.info(f"Vector Search | {search_time:.3f}s | top_k={top_k} | results={results_count}")

def log_llm_call(prompt: str, response: str, llm_time: float, token_count: int):
    """Log LLM call details"""
    _metrics["llm_times"].append(llm_time)
    _metrics["token_usage"].append(token_count)
    logger.info(f"LLM Call | {llm_time:.3f}s | tokens={token_count}")

def get_metrics() -> Dict[str, Any]:
    """Get current metrics"""
    uptime = time.time() - _metrics["start_time"]
    avg_response_time = (_metrics["total_response_time"] / _metrics["total_queries"]) * 1000 if _metrics["total_queries"] > 0 else 0
    
    return {
        "total_queries": _metrics["total_queries"],
        "avg_response_time_ms": round(avg_response_time, 2),
        "uptime_seconds": round(uptime, 2),
        "avg_vector_search_time": round(sum(_metrics["vector_search_times"]) / len(_metrics["vector_search_times"]), 3) if _metrics["vector_search_times"] else 0,
        "avg_llm_time": round(sum(_metrics["llm_times"]) / len(_metrics["llm_times"]), 3) if _metrics["llm_times"] else 0,
        "total_tokens_used": sum(_metrics["token_usage"])
    }

def count_tokens(text: str) -> int:
    """Count tokens in text using tiktoken or fallback"""
    if TIKTOKEN_AVAILABLE:
        try:
            encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
            return len(encoding.encode(text))
        except:
            pass
    
    # Fallback: rough estimation based on words
    return len(text.split())

def validate_api_key(api_key: str) -> bool:
    """Validate API key"""
    expected_key = os.getenv("API_KEY")
    return api_key == expected_key

def create_chunk_id(doc_name: str, chunk_index: int) -> str:
    """Create unique chunk ID"""
    return f"{doc_name}_{chunk_index}"

def format_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()

def safe_json_dumps(obj: Any) -> str:
    """Safely serialize object to JSON"""
    try:
        return json.dumps(obj, default=str)
    except:
        return str(obj) 