"""
Canva Credentials Service
Manages Canva OAuth tokens in the database
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .db import SessionLocal
from .models import CanvaCredentials

# Configure logger
logger = logging.getLogger(__name__)

class CanvaCredentialsService:
    """Service for managing Canva OAuth credentials in database"""
    
    def __init__(self):
        pass
    
    def save_credentials(self, user_id: str, token_data: Dict[str, Any]) -> bool:
        """
        Save Canva credentials to database
        
        Args:
            user_id: User identifier
            token_data: Token data from OAuth flow
            
        Returns:
            True if saved successfully
        """
        try:
            db = SessionLocal()
            # Check if credentials already exist
            existing = db.query(CanvaCredentials).filter(
                CanvaCredentials.user_id == user_id
            ).first()
            
            # Calculate expiration time
            expires_in = token_data.get('expires_in', 3600)  # Default 1 hour
            expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            if existing:
                # Update existing credentials
                existing.access_token = token_data.get('access_token', '')
                existing.refresh_token = token_data.get('refresh_token', existing.refresh_token)
                existing.expires_at = expires_at
                existing.token_type = token_data.get('token_type', 'Bearer')
                existing.scope = token_data.get('scope', '')
                existing.updated_at = datetime.now()
            else:
                # Create new credentials
                import uuid
                credentials = CanvaCredentials(
                    id=f"canva_{user_id}_{uuid.uuid4()}",
                    user_id=user_id,
                    access_token=token_data.get('access_token', ''),
                    refresh_token=token_data.get('refresh_token', ''),
                    expires_at=expires_at,
                    token_type=token_data.get('token_type', 'Bearer'),
                    scope=token_data.get('scope', ''),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.add(credentials)
            
            db.commit()
            logger.info(f"Canva credentials saved successfully", extra={"user_id": user_id})
            return True
                
        except Exception as e:
            logger.error(f"Failed to save Canva credentials", extra={"user_id": user_id, "error": str(e)})
            return False
        finally:
            db.close()
    
    def get_credentials(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get Canva credentials from database
        
        Args:
            user_id: User identifier
            
        Returns:
            Credentials dictionary or None
        """
        try:
            db = SessionLocal()
            credentials = db.query(CanvaCredentials).filter(
                CanvaCredentials.user_id == user_id
            ).first()
            
            if not credentials:
                return None
            
            return {
                'user_id': credentials.user_id,
                'access_token': credentials.access_token,
                'refresh_token': credentials.refresh_token,
                'expires_at': credentials.expires_at.isoformat() if credentials.expires_at else None,
                'token_type': credentials.token_type,
                'scope': credentials.scope,
                'created_at': credentials.created_at.isoformat() if credentials.created_at else None,
                'updated_at': credentials.updated_at.isoformat() if credentials.updated_at else None
            }
            
        except Exception as e:
            logger.error(f"Failed to retrieve Canva credentials", extra={"user_id": user_id, "error": str(e)})
            return None
        finally:
            db.close()
    
    def is_token_valid(self, user_id: str) -> bool:
        """
        Check if Canva token is valid and not expired
        
        Args:
            user_id: User identifier
            
        Returns:
            True if token is valid
        """
        try:
            credentials = self.get_credentials(user_id)
            if not credentials:
                return False
            
            # Check if token is expired
            expires_at = credentials.get('expires_at')
            if expires_at:
                expires_datetime = datetime.fromisoformat(expires_at)
                if datetime.now() >= expires_datetime:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check Canva token validity", extra={"user_id": user_id, "error": str(e)})
            return False
    
    def refresh_token(self, user_id: str) -> bool:
        """
        Refresh Canva access token
        
        Args:
            user_id: User identifier
            
        Returns:
            True if refreshed successfully
        """
        try:
            credentials = self.get_credentials(user_id)
            if not credentials or not credentials.get('refresh_token'):
                return False
            
            # Import Canva integration
            from .canva_integration import CanvaIntegration
            
            # Initialize Canva integration with stored tokens
            canva = CanvaIntegration()
            canva.access_token = credentials.get('access_token')
            canva.refresh_token = credentials.get('refresh_token')
            
            # Refresh token
            refreshed_data = canva.refresh_access_token()
            
            # Save refreshed credentials
            return self.save_credentials(user_id, refreshed_data)
            
        except Exception as e:
            logger.error(f"Failed to refresh Canva token", extra={"user_id": user_id, "error": str(e)})
            return False
    
    def delete_credentials(self, user_id: str) -> bool:
        """
        Delete Canva credentials from database
        
        Args:
            user_id: User identifier
            
        Returns:
            True if deleted successfully
        """
        try:
            db = SessionLocal()
            credentials = db.query(CanvaCredentials).filter(
                CanvaCredentials.user_id == user_id
            ).first()
            
            if credentials:
                db.delete(credentials)
                db.commit()
                logger.info(f"Canva credentials deleted successfully", extra={"user_id": user_id})
                return True
            else:
                logger.warning(f"No Canva credentials found for deletion", extra={"user_id": user_id})
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete Canva credentials", extra={"user_id": user_id, "error": str(e)})
            return False
        finally:
            db.close()
    
    def get_access_token(self, user_id: str) -> Optional[str]:
        """
        Get valid access token (refreshes if needed)
        
        Args:
            user_id: User identifier
            
        Returns:
            Access token or None
        """
        try:
            if not self.is_token_valid(user_id):
                # Try to refresh token
                if not self.refresh_token(user_id):
                    return None
            
            credentials = self.get_credentials(user_id)
            return credentials.get('access_token') if credentials else None
            
        except Exception as e:
            logger.error(f"Failed to get Canva access token", extra={"user_id": user_id, "error": str(e)})
            return None

# Global instance
canva_credentials_service = CanvaCredentialsService()
