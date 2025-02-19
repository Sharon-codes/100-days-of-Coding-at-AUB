"""
Rate limiter implementation for API requests
"""
import time
import logging
from typing import List, Dict
import asyncio

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    A simple token bucket rate limiter
    
    This implementation tracks request counts in a sliding window.
    """
    def __init__(self, max_requests: int = 60, time_window: int = 60):
        """
        Initialize the rate limiter
        
        Args:
            max_requests: Maximum number of requests allowed in the time window
            time_window: Time window in seconds (default: 60s = 1 minute)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.request_timestamps: List[float] = []
        self._lock = asyncio.Lock()
        
    async def is_allowed(self) -> bool:
        """
        Check if a new request is allowed based on the rate limit.
        Also removes timestamps older than the time window.
        
        Returns:
            bool: True if request is allowed, False otherwise
        """
        current_time = time.time()
        
        async with self._lock:
            # Remove timestamps older than the time window
            while self.request_timestamps and self.request_timestamps[0] < current_time - self.time_window:
                self.request_timestamps.pop(0)
                
            # Check if we're at the limit
            if len(self.request_timestamps) >= self.max_requests:
                logger.warning(f"Rate limit reached: {len(self.request_timestamps)} requests in last {self.time_window}s")
                return False
                
            # Record this request's timestamp
            self.request_timestamps.append(current_time)
            return True
            
    async def wait_if_needed(self) -> float:
        """
        Wait if necessary to stay within rate limits
        
        Returns:
            float: The time waited in seconds, or 0 if no wait was needed
        """
        async with self._lock:
            if len(self.request_timestamps) < self.max_requests:
                self.request_timestamps.append(time.time())
                return 0
                
            # Calculate how long we need to wait
            oldest_timestamp = self.request_timestamps[0]
            current_time = time.time()
            wait_time = (oldest_timestamp + self.time_window) - current_time
            
            if wait_time > 0:
                logger.info(f"Rate limit: waiting {wait_time:.2f} seconds before next request")
                await asyncio.sleep(wait_time)
                
                # After waiting, we remove the oldest timestamp and add our new one
                self.request_timestamps.pop(0)
                self.request_timestamps.append(time.time())
                return wait_time
                
            # If we don't need to wait, just update timestamps
            self.request_timestamps.pop(0)
            self.request_timestamps.append(time.time())
            return 0


class PerEndpointRateLimiter:
    """
    A rate limiter that tracks limits separately for different endpoints or keys
    """
    def __init__(self, max_requests: int = 60, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.limiters: Dict[str, RateLimiter] = {}
        self._lock = asyncio.Lock()
        
    async def is_allowed(self, key: str) -> bool:
        """Check if a request for the specified key is allowed"""
        async with self._lock:
            if key not in self.limiters:
                self.limiters[key] = RateLimiter(self.max_requests, self.time_window)
                
        return await self.limiters[key].is_allowed()
        
    async def wait_if_needed(self, key: str) -> float:
        """Wait if needed for the specified key"""
        async with self._lock:
            if key not in self.limiters:
                self.limiters[key] = RateLimiter(self.max_requests, self.time_window)
                
        return await self.limiters[key].wait_if_needed()