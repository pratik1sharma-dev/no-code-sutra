"""
Rate limiting middleware for FastAPI
"""
from fastapi import HTTPException, Request
from typing import Dict, Optional
import time
import asyncio
from collections import defaultdict, deque
import os

class RateLimitExceeded(HTTPException):
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(status_code=429, detail=detail)

class RateLimiter:
    def __init__(self):
        # Store request timestamps for each identifier
        self.requests: Dict[str, deque] = defaultdict(lambda: deque())
        # Store blocked users and their unblock time
        self.blocked_until: Dict[str, float] = {}
        
        # Rate limiting configuration
        self.limits = {
            "default": {"requests": 100, "window": 3600},  # 100 requests per hour
            "auth": {"requests": 10, "window": 300},       # 10 auth attempts per 5 minutes
            "workflow": {"requests": 50, "window": 3600},  # 50 workflow executions per hour
            "api_key": {"requests": 1000, "window": 3600}, # Higher limit for API key users
        }
        
        # Cleanup interval
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5 minutes

    def _cleanup_old_requests(self):
        """Remove old request records to prevent memory leaks"""
        current_time = time.time()
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        self.last_cleanup = current_time
        
        # Clean up old requests
        for identifier in list(self.requests.keys()):
            request_times = self.requests[identifier]
            # Remove requests older than the largest window (1 hour)
            cutoff_time = current_time - 3600
            while request_times and request_times[0] < cutoff_time:
                request_times.popleft()
            
            # Remove empty deques
            if not request_times:
                del self.requests[identifier]
        
        # Clean up expired blocks
        expired_blocks = [
            identifier for identifier, unblock_time in self.blocked_until.items()
            if current_time > unblock_time
        ]
        for identifier in expired_blocks:
            del self.blocked_until[identifier]

    def _get_rate_limit_config(self, endpoint_type: str, has_api_key: bool = False) -> dict:
        """Get rate limit configuration for endpoint type"""
        if has_api_key:
            return self.limits["api_key"]
        return self.limits.get(endpoint_type, self.limits["default"])

    def _is_blocked(self, identifier: str) -> bool:
        """Check if identifier is currently blocked"""
        if identifier in self.blocked_until:
            if time.time() < self.blocked_until[identifier]:
                return True
            else:
                del self.blocked_until[identifier]
        return False

    def _block_user(self, identifier: str, duration: int = 300):
        """Block user for specified duration (default 5 minutes)"""
        self.blocked_until[identifier] = time.time() + duration

    def check_rate_limit(self, identifier: str, endpoint_type: str = "default", has_api_key: bool = False) -> bool:
        """Check if request should be allowed"""
        self._cleanup_old_requests()
        
        # Check if user is blocked
        if self._is_blocked(identifier):
            return False
        
        current_time = time.time()
        config = self._get_rate_limit_config(endpoint_type, has_api_key)
        window_start = current_time - config["window"]
        
        # Get request times for this identifier
        request_times = self.requests[identifier]
        
        # Remove old requests outside the window
        while request_times and request_times[0] < window_start:
            request_times.popleft()
        
        # Check if limit exceeded
        if len(request_times) >= config["requests"]:
            # Block user for repeated violations
            if len(request_times) >= config["requests"] * 1.5:
                self._block_user(identifier, 900)  # 15 minutes
            return False
        
        # Add current request
        request_times.append(current_time)
        return True

    def get_rate_limit_info(self, identifier: str, endpoint_type: str = "default", has_api_key: bool = False) -> dict:
        """Get current rate limit status"""
        config = self._get_rate_limit_config(endpoint_type, has_api_key)
        current_time = time.time()
        window_start = current_time - config["window"]
        
        request_times = self.requests[identifier]
        recent_requests = sum(1 for t in request_times if t > window_start)
        
        remaining = max(0, config["requests"] - recent_requests)
        reset_time = int(current_time + config["window"])
        
        return {
            "limit": config["requests"],
            "remaining": remaining,
            "reset": reset_time,
            "window": config["window"]
        }

# Global rate limiter instance
rate_limiter = RateLimiter()

async def apply_rate_limit(request: Request, identifier: str, endpoint_type: str = "default", has_api_key: bool = False):
    """Apply rate limiting to a request"""
    if not rate_limiter.check_rate_limit(identifier, endpoint_type, has_api_key):
        rate_info = rate_limiter.get_rate_limit_info(identifier, endpoint_type, has_api_key)
        raise RateLimitExceeded(
            detail=f"Rate limit exceeded. Limit: {rate_info['limit']} requests per {rate_info['window']} seconds. "
                   f"Try again after {rate_info['reset']}"
        )
    
    # Add rate limit headers to response (will be added by middleware)
    rate_info = rate_limiter.get_rate_limit_info(identifier, endpoint_type, has_api_key)
    request.state.rate_limit_info = rate_info
