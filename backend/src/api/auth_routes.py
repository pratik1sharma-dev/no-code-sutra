"""
Authentication routes for the API
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import hashlib
import secrets

from middleware.auth import create_access_token, get_user_identifier
from middleware.rate_limiter import apply_rate_limit
from config.security import security_config

router = APIRouter(prefix="/api/auth", tags=["authentication"])

class LoginRequest(BaseModel):
    username: str
    password: str
    
class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_id: str

class ApiKeyRequest(BaseModel):
    name: str
    description: Optional[str] = ""

class ApiKeyResponse(BaseModel):
    api_key: str
    name: str
    created_at: str

# Simple in-memory user store for demo (replace with database in production)
DEMO_USERS = {
    "admin": {
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "permissions": ["admin"],
        "user_id": "admin_user"
    },
    "user": {
        "password_hash": hashlib.sha256("user123".encode()).hexdigest(), 
        "permissions": ["workflow_execute", "workflow_read"],
        "user_id": "demo_user"
    }
}

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    return hashlib.sha256(password.encode()).hexdigest() == password_hash

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, http_request: Request):
    """Login endpoint to get JWT token"""
    try:
        # Apply rate limiting for auth endpoints
        if security_config.RATE_LIMIT_ENABLED:
            identifier = get_user_identifier(http_request, None)
            await apply_rate_limit(http_request, identifier, "auth", False)
        
        # Check if user exists
        user_data = DEMO_USERS.get(request.username)
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify password
        if not verify_password(request.password, user_data["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create JWT token
        token_data = {
            "sub": user_data["user_id"],
            "username": request.username,
            "permissions": user_data["permissions"]
        }
        
        expires_delta = timedelta(hours=security_config.JWT_EXPIRATION_HOURS)
        access_token = create_access_token(token_data, expires_delta)
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=int(expires_delta.total_seconds()),
            user_id=user_data["user_id"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.post("/generate-api-key", response_model=ApiKeyResponse)
async def generate_api_key(request: ApiKeyRequest, http_request: Request):
    """Generate a new API key (demo endpoint)"""
    try:
        # Apply rate limiting
        if security_config.RATE_LIMIT_ENABLED:
            identifier = get_user_identifier(http_request, None)
            await apply_rate_limit(http_request, identifier, "auth", False)
        
        # Generate API key
        api_key = secrets.token_urlsafe(32)
        
        return ApiKeyResponse(
            api_key=api_key,
            name=request.name,
            created_at=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API key generation failed: {str(e)}")

@router.get("/demo-credentials")
async def get_demo_credentials():
    """Get demo credentials for testing (remove in production)"""
    if security_config.is_production():
        raise HTTPException(status_code=404, detail="Not found")
    
    return {
        "message": "Demo credentials for testing",
        "users": [
            {
                "username": "admin",
                "password": "admin123",
                "permissions": ["admin"],
                "description": "Admin user with full access"
            },
            {
                "username": "user", 
                "password": "user123",
                "permissions": ["workflow_execute", "workflow_read"],
                "description": "Regular user with limited access"
            }
        ],
        "master_api_key": security_config.MASTER_API_KEY[:10] + "..." if security_config.MASTER_API_KEY else "Not configured"
    }
