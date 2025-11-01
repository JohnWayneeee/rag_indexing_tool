"""
Module for caching using LRU cache
"""
import logging
from functools import lru_cache
from typing import Any, Optional, Callable
import hashlib
import json

logger = logging.getLogger(__name__)


class LRUCache:
    """LRU cache for storing computation results"""
    
    def __init__(self, maxsize: int = 128):
        """
        Args:
            maxsize: Maximum number of elements in cache
        """
        self.maxsize = maxsize
        self.cache = {}
        self.access_order = []  # For tracking access order
    
    def _make_key(self, *args, **kwargs) -> str:
        """Create key from arguments"""
        try:
            # Serialize arguments to JSON string
            key_data = {
                'args': args,
                'kwargs': kwargs
            }
            key_str = json.dumps(key_data, sort_keys=True, default=str)
            # Create hash for compactness
            return hashlib.md5(key_str.encode()).hexdigest()
        except Exception as e:
            logger.warning(f"Error creating cache key: {e}")
            return str(hash(str(args) + str(kwargs)))
    
    def get(self, *args, **kwargs) -> Optional[Any]:
        """Get value from cache"""
        key = self._make_key(*args, **kwargs)
        
        if key in self.cache:
            # Update access order
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        
        return None
    
    def set(self, value: Any, *args, **kwargs):
        """Set value in cache"""
        key = self._make_key(*args, **kwargs)
        
        # If cache is full, remove oldest element
        if len(self.cache) >= self.maxsize and key not in self.cache:
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]
            logger.debug(f"Removed stale cache element: {oldest_key[:8]}...")
        
        # Add new element
        self.cache[key] = value
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()
        self.access_order.clear()
        logger.info("Cache cleared")
    
    def size(self) -> int:
        """Return current cache size"""
        return len(self.cache)


# Global caches for different data types
_embedding_cache = LRUCache(maxsize=256)  # Cache for embeddings
_query_cache = LRUCache(maxsize=128)  # Cache for search results


def get_embedding_cache() -> LRUCache:
    """Return cache for embeddings"""
    return _embedding_cache


def get_query_cache() -> LRUCache:
    """Return cache for search results"""
    return _query_cache


def cached_embedding(func: Callable) -> Callable:
    """Decorator for caching embedding creation results"""
    def wrapper(text: str, *args, **kwargs):
        cache = get_embedding_cache()
        cached = cache.get(text)
        
        if cached is not None:
            logger.debug(f"Embedding found in cache for text of length {len(text)}")
            return cached
        
        result = func(text, *args, **kwargs)
        cache.set(result, text)
        return result
    
    return wrapper


def cached_query(func: Callable) -> Callable:
    """Decorator for caching search results"""
    def wrapper(query: str, *args, **kwargs):
        cache = get_query_cache()
        # Create key from query and search parameters
        cache_key = (query, tuple(args), tuple(sorted(kwargs.items())))
        cached = cache.get(*cache_key)
        
        if cached is not None:
            logger.debug(f"Search result found in cache for query: {query[:50]}...")
            return cached
        
        result = func(query, *args, **kwargs)
        cache.set(result, *cache_key)
        return result
    
    return wrapper

