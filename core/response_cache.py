"""Response caching for common queries."""

import hashlib
import json
from typing import Optional, Dict
from collections import OrderedDict
from config.settings import MAX_CACHE_SIZE, CACHE_ENABLED


class ResponseCache:
    """LRU cache for API responses to reduce latency."""
    
    def __init__(self, max_size: int = MAX_CACHE_SIZE):
        """
        Initialize response cache.
        
        Args:
            max_size: Maximum number of cached responses
        """
        self.max_size = max_size
        self.cache: OrderedDict = OrderedDict()
        self.enabled = CACHE_ENABLED
    
    def _hash_query(self, query: str, personality_hash: Optional[str] = None) -> str:
        """
        Generate hash for query.
        
        Args:
            query: User query
            personality_hash: Optional personality settings hash
            
        Returns:
            Hash string
        """
        key = query.lower().strip()
        if personality_hash:
            key += personality_hash
        
        return hashlib.md5(key.encode()).hexdigest()
    
    def get(self, query: str, personality_hash: Optional[str] = None) -> Optional[str]:
        """
        Get cached response if available.
        
        Args:
            query: User query
            personality_hash: Optional personality settings hash
            
        Returns:
            Cached response or None
        """
        if not self.enabled:
            return None
        
        cache_key = self._hash_query(query, personality_hash)
        
        if cache_key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(cache_key)
            return self.cache[cache_key]
        
        return None
    
    def set(self, query: str, response: str, personality_hash: Optional[str] = None):
        """
        Cache a response.
        
        Args:
            query: User query
            response: API response
            personality_hash: Optional personality settings hash
        """
        if not self.enabled:
            return
        
        cache_key = self._hash_query(query, personality_hash)
        
        # Add or update
        self.cache[cache_key] = response
        self.cache.move_to_end(cache_key)
        
        # Remove oldest if over limit
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)
    
    def clear(self):
        """Clear all cached responses."""
        self.cache.clear()
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'enabled': self.enabled
        }
    
    def enable(self):
        """Enable caching."""
        self.enabled = True
    
    def disable(self):
        """Disable caching."""
        self.enabled = False





