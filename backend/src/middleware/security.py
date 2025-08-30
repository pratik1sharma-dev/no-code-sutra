"""
Security middleware for FastAPI - Headers, CORS, and input validation
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import re
import json
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # HSTS (only in production with HTTPS)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https:; "
            "font-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response.headers["Content-Security-Policy"] = csp
        
        # Add rate limit headers if available
        if hasattr(request.state, 'rate_limit_info'):
            rate_info = request.state.rate_limit_info
            response.headers["X-RateLimit-Limit"] = str(rate_info['limit'])
            response.headers["X-RateLimit-Remaining"] = str(rate_info['remaining'])
            response.headers["X-RateLimit-Reset"] = str(rate_info['reset'])
        
        return response

class InputValidationMiddleware(BaseHTTPMiddleware):
    """Validate and sanitize input data"""
    
    # Suspicious patterns that might indicate attacks
    SUSPICIOUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # XSS
        r'javascript:',                # XSS
        r'on\w+\s*=',                 # Event handlers
        r'union\s+select',            # SQL injection
        r'drop\s+table',              # SQL injection
        r'insert\s+into',             # SQL injection
        r'delete\s+from',             # SQL injection
        r'\.\./\.\.',                 # Path traversal
        r'file://',                   # File inclusion
        r'data:text/html',            # Data URI XSS
    ]
    
    # Compile patterns for better performance
    COMPILED_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in SUSPICIOUS_PATTERNS]
    
    async def dispatch(self, request: Request, call_next):
        # Skip validation for certain endpoints
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Validate request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
            return JSONResponse(
                status_code=413,
                content={"error": "Request too large"}
            )
        
        # Validate content type for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if not content_type.startswith(("application/json", "multipart/form-data")):
                return JSONResponse(
                    status_code=415,
                    content={"error": "Unsupported media type"}
                )
        
        # Read and validate request body
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    # Try to parse as JSON
                    if content_type.startswith("application/json"):
                        try:
                            json_data = json.loads(body.decode())
                            if self._contains_suspicious_content(json_data):
                                logger.warning(f"Suspicious content detected from {request.client.host}")
                                return JSONResponse(
                                    status_code=400,
                                    content={"error": "Invalid input detected"}
                                )
                        except json.JSONDecodeError:
                            return JSONResponse(
                                status_code=400,
                                content={"error": "Invalid JSON"}
                            )
                
                # Recreate request with validated body
                async def receive():
                    return {"type": "http.request", "body": body}
                
                request._receive = receive
                
            except Exception as e:
                logger.error(f"Error validating request: {e}")
                return JSONResponse(
                    status_code=400,
                    content={"error": "Request validation failed"}
                )
        
        return await call_next(request)
    
    def _contains_suspicious_content(self, data: Any) -> bool:
        """Check if data contains suspicious patterns"""
        if isinstance(data, str):
            return any(pattern.search(data) for pattern in self.COMPILED_PATTERNS)
        elif isinstance(data, dict):
            return any(self._contains_suspicious_content(v) for v in data.values())
        elif isinstance(data, list):
            return any(self._contains_suspicious_content(item) for item in data)
        return False

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log security-relevant requests"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request details
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # Log suspicious activity
        if response.status_code in [401, 403, 429]:
            logger.warning(
                f"Security event: {response.status_code} - "
                f"IP: {client_ip} - "
                f"Path: {request.url.path} - "
                f"Method: {request.method} - "
                f"User-Agent: {user_agent}"
            )
        
        # Log slow requests (potential DoS)
        if process_time > 10:  # 10 seconds
            logger.warning(
                f"Slow request: {process_time:.2f}s - "
                f"IP: {client_ip} - "
                f"Path: {request.url.path}"
            )
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get real client IP considering proxies"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return getattr(request.client, 'host', 'unknown')

import time
