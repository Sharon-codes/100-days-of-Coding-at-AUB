"""
Asynchronous cache manager implementation
"""
import asyncio
import time
from typing import Any, Dict, Optional, Set
import logging

logger = logging.getLogger(__name__)

class AsyncCacheManager:
    """
    An asynchronous cache manager that provides get/set operations
    with TTL (time-to-live) expiration.
    """
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        self._cleaner_task = None
        
    async def start(self):
        """Start the background cleaner task."""
        if self._cleaner_task is None:
            self._cleaner_task = asyncio.create_task(self._clean_expired_entries())
            
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache if it exists and isn't expired"""
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
                
            # Check if entry is expired
            if entry["expiry"] < time.time():
                del self._cache[key]
                return None
                
            return entry["value"]
            
    async def set(self, key: str, value: Any, expiry: int = 300) -> None:
        """
        Add or update a cache entry
        
        Args:
            key: The cache key
            value: The value to store
            expiry: Time to live in seconds (default 300s/5min)
        """
        async with self._lock:
            self._cache[key] = {
                "value": value,
                "expiry": time.time() + expiry,
            }
            
    async def delete(self, key: str) -> bool:
        """Delete a key from the cache, return True if key existed"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
            
    async def clear(self) -> None:
        """Clear all entries from the cache"""
        async with self._lock:
            self._cache.clear()
            
    async def _clean_expired_entries(self) -> None:
        """Background task that periodically removes expired entries"""
        try:
            while True:
                await asyncio.sleep(60)  # Run every minute
                keys_to_delete: Set[str] = set()
                current_time = time.time()
                
                # First, identify expired keys
                async with self._lock:
                    for key, entry in self._cache.items():
                        if entry["expiry"] < current_time:
                            keys_to_delete.add(key)
                
                # Then delete them if they're still expired
                if keys_to_delete:
                    async with self._lock:
                        for key in keys_to_delete:
                            if key in self._cache and self._cache[key]["expiry"] < current_time:
                                del self._cache[key]
                    logger.info(f"Cleaned {len(keys_to_delete)} expired cache entries")
                    
        except asyncio.CancelledError:
            logger.info("Cache cleaner task was cancelled")
        except Exception as e:
            logger.error(f"Unexpected error in cache cleaner: {str(e)}")
            
    def stop(self):
        """Cancel the cleaner task if it exists and is running"""
        if self._cleaner_task and not self._cleaner_task.done():
            self._cleaner_task.cancel()
            
    def __del__(self):
        """Clean up resources when the object is destroyed"""
        if hasattr(self, "_cleaner_task") and self._cleaner_task and not self._cleaner_task.done():
            self._cleaner_task.cancel()