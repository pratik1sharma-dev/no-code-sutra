"""
Security configuration and utilities
"""
import os
from typing import List, Optional
import secrets

class SecurityConfig:
    """Centralized security configuration"""
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # JWT Configuration
    JWT_SECRET = os.getenv("JWT_SECRET")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 24
    
    # API Key Configuration
    MASTER_API_KEY = os.getenv("MASTER_API_KEY")
    
    # CORS Configuration
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else [
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://localhost:5174",
        "http://localhost:5175",
        "https://no-code-sutra.vercel.app",
        "https://no-code-sutra-production.up.railway.app"
    ]
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    DEFAULT_RATE_LIMIT = int(os.getenv("DEFAULT_RATE_LIMIT", "100"))
    AUTH_RATE_LIMIT = int(os.getenv("AUTH_RATE_LIMIT", "10"))
    WORKFLOW_RATE_LIMIT = int(os.getenv("WORKFLOW_RATE_LIMIT", "50"))
    
    # Security Headers
    ENABLE_SECURITY_HEADERS = True
    ENABLE_CORS_CREDENTIALS = os.getenv("ENABLE_CORS_CREDENTIALS", "true").lower() == "true"
    
    # Session Configuration
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "true").lower() == "true"
    SESSION_COOKIE_HTTPONLY = os.getenv("SESSION_COOKIE_HTTPONLY", "true").lower() == "true"
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "strict")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    SECURITY_LOG_ENABLED = os.getenv("SECURITY_LOG_ENABLED", "true").lower() == "true"
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """Validate security configuration and return any issues"""
        issues = []
        
        if not cls.JWT_SECRET:
            issues.append("JWT_SECRET not set - using insecure default")
        elif len(cls.JWT_SECRET) < 32:
            issues.append("JWT_SECRET too short - should be at least 32 characters")
        
        if not cls.MASTER_API_KEY:
            issues.append("MASTER_API_KEY not set - API key authentication disabled")
        
        if cls.ENVIRONMENT == "production":
            if cls.DEBUG:
                issues.append("DEBUG should be disabled in production")
            
            if "localhost" in str(cls.ALLOWED_ORIGINS):
                issues.append("Localhost origins should not be allowed in production")
            
            if not cls.SESSION_COOKIE_SECURE:
                issues.append("SESSION_COOKIE_SECURE should be enabled in production")
        
        return issues
    
    @classmethod
    def generate_secure_keys(cls) -> dict:
        """Generate secure keys for configuration"""
        return {
            "JWT_SECRET": secrets.token_urlsafe(64),
            "MASTER_API_KEY": secrets.token_urlsafe(32),
        }
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production"""
        return cls.ENVIRONMENT == "production"
    
    @classmethod
    def get_cors_config(cls) -> dict:
        """Get CORS configuration"""
        return {
            "allow_origins": cls.ALLOWED_ORIGINS,
            "allow_credentials": cls.ENABLE_CORS_CREDENTIALS,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": [
                "Authorization",
                "Content-Type", 
                "X-API-Key",
                "X-Requested-With",
                "Accept",
                "Origin",
                "User-Agent"
            ],
            "expose_headers": [
                "X-RateLimit-Limit",
                "X-RateLimit-Remaining", 
                "X-RateLimit-Reset"
            ]
        }

# Initialize configuration
security_config = SecurityConfig()

# Validate configuration on import
config_issues = security_config.validate_config()
if config_issues:
    import logging
    logger = logging.getLogger(__name__)
    for issue in config_issues:
        logger.warning(f"Security configuration issue: {issue}")
