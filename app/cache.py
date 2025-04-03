import time
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class Cache:
    """Simple in-memory cache implementation with TTL"""
    
    def __init__(self, default_ttl: int = 300):
        """
        Initialize the cache
        
        Args:
            default_ttl: Default time-to-live in seconds for cache entries
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        logger.info(f"Cache initialized with default TTL of {default_ttl} seconds")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache
        
        Args:
            key: Cache key
            
        Returns:
            The cached value if it exists and is not expired, None otherwise
        """
        if key not in self.cache:
            return None
            
        cached_item = self.cache[key]
        current_time = time.time()
        
        # Check if the cached item has expired
        if current_time > cached_item["expires_at"]:
            # Remove expired item
            del self.cache[key]
            return None
            
        return cached_item["value"]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in the cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds, defaults to self.default_ttl
        """
        if ttl is None:
            ttl = self.default_ttl
            
        expires_at = time.time() + ttl
        
        self.cache[key] = {
            "value": value,
            "expires_at": expires_at
        }
    
    def clear(self) -> None:
        """Clear all items from the cache"""
        self.cache.clear()
        
    def remove(self, key: str) -> None:
        """Remove a specific key from the cache"""
        if key in self.cache:
            del self.cache[key]
            
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        current_time = time.time()
        total_items = len(self.cache)
        expired_items = sum(1 for item in self.cache.values() 
                          if current_time > item["expires_at"])
                          
        return {
            "total_items": total_items,
            "expired_items": expired_items,
            "active_items": total_items - expired_items
        }