import asyncio
import logging
import re
from typing import List, Dict, Any
import random
from .metrics import search_result_count

logger = logging.getLogger(__name__)

class SearchService:
    """Service for handling search operations"""
    
    def __init__(self):
        self.data = []
        self.initialized = False
    
    def load_data(self, data: List[Dict[str, Any]]):
        """Load data into the search service"""
        self.data = data
        self.initialized = True
        logger.info(f"Loaded {len(data)} items into search service")
    
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for items matching the query
        
        Args:
            query: The search query string
            limit: Maximum number of results to return
            
        Returns:
            List of matching items
        """
        if not self.initialized or not self.data:
            logger.warning("Search called but no data is loaded")
            return []
            
        # Simple case-insensitive search implementation
        query = query.lower()
        results = []
        
        # Simulate some processing delay
        await asyncio.sleep(random.uniform(0.05, 0.3))
        
        for item in self.data:
            # Check if query matches any field in the item
            for value in item.values():
                if isinstance(value, str) and query in value.lower():
                    results.append(item)
                    break
                    
            if len(results) >= limit:
                break
        
        # Record the result count metric
        search_result_count.observe(len(results))
        
        return results[:limit]