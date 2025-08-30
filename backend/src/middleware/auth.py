"""
Authentication and Authorization middleware for FastAPI
"""
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
import jwt
import os
from datetime import datetime, timedelta
import hashlib
import secrets

# Security configuration
JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# API Key configuration
API_KEY_HEADER = "X-API-Key"
MASTER_API_KEY = os.getenv("MASTER_API_KEY")

security = HTTPBearer(auto_error=False)

class AuthenticationError(HTTPException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=401, detail=detail)

class AuthorizationError(HTTPException):
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(status_code=403, detail=detail)

def generate_api_key() -> str:
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)

def hash_api_key(api_key: str) -> str:
    """Hash an API key for secure storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()

def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """Verify an API key against its hash"""
    return hashlib.sha256(api_key.encode()).hexdigest() == hashed_key

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.JWTError:
        raise AuthenticationError("Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    if not credentials:
        raise AuthenticationError("Authorization header required")
    
    try:
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid token payload")
        return {"user_id": user_id, "permissions": payload.get("permissions", [])}
    except Exception as e:
        raise AuthenticationError(str(e))

async def get_api_key_auth(request: Request):
    """Authenticate using API key"""
    api_key = request.headers.get(API_KEY_HEADER)
    if not api_key:
        raise AuthenticationError("API key required")
    
    # Check master API key
    if MASTER_API_KEY and api_key == MASTER_API_KEY:
        return {"user_id": "system", "permissions": ["admin"]}
    
    # TODO: Implement database lookup for user API keys
    # For now, reject unknown API keys
    raise AuthenticationError("Invalid API key")

async def optional_auth(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Optional authentication - returns user if authenticated, None otherwise"""
    try:
        if credentials:
            return await get_current_user(credentials)
        
        # Try API key authentication
        api_key = request.headers.get(API_KEY_HEADER)
        if api_key:
            return await get_api_key_auth(request)
        
        return None
    except:
        return None

def require_permissions(required_permissions: List[str]):
    """Decorator to require specific permissions"""
    def permission_checker(user: dict = Depends(get_current_user)):
        user_permissions = user.get("permissions", [])
        
        # Admin permission grants all access
        if "admin" in user_permissions:
            return user
        
        # Check if user has all required permissions
        if not all(perm in user_permissions for perm in required_permissions):
            raise AuthorizationError(f"Required permissions: {required_permissions}")
        
        return user
    
    return permission_checker

def require_api_key():
    """Require API key authentication"""
    return Depends(get_api_key_auth)

# Rate limiting user tracking
user_request_counts = {}

def get_user_identifier(request: Request, user: Optional[dict] = None) -> str:
    """Get unique identifier for rate limiting"""
    if user:
        return f"user:{user['user_id']}"
    
    # Fall back to IP address
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return f"ip:{forwarded_for.split(',')[0].strip()}"
    
    client_host = getattr(request.client, 'host', 'unknown')
    return f"ip:{client_host}"
