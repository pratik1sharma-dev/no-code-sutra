import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .db import SessionLocal
from .models import InstagramCredentials

# Configure logger
logger = logging.getLogger(__name__)


class InstagramCredentialsService:
    """Service for managing Instagram credentials in the database"""
    
    def __init__(self):
        pass
    
    def save_credentials(self, user_id: str, token_data: Dict[str, Any]) -> bool:
        """
        Save Instagram credentials to database
        
        Args:
            user_id: User identifier
            token_data: Token data from OAuth flow
            
        Returns:
            True if saved successfully
        """
        try:

            logger.info("Saving Instagram credentials", extra={"user_id": user_id, "token_keys": list(token_data.keys())})
            
            db = SessionLocal()
            logger.debug("Database session created", extra={"user_id": user_id})
            
            # Check if credentials already exist for this user
            existing = db.query(InstagramCredentials).filter(
                InstagramCredentials.user_id == user_id
            ).first()
            
            logger.debug("Checked for existing credentials", extra={"user_id": user_id, "exists": existing is not None})
            
            if existing:
                logger.info("Updating existing Instagram credentials", extra={"user_id": user_id})
                # Update existing credentials
                existing.access_token = token_data['access_token']
                existing.token_type = token_data['token_type']
                existing.expires_at = datetime.fromisoformat(token_data['expires_at'])
                existing.updated_at = datetime.utcnow()
                
                # Update Instagram account info if available
                if token_data.get('instagram_accounts'):
                    account = token_data['instagram_accounts'][0]
                    existing.instagram_business_account_id = account['instagram_account']['id']
                    existing.page_id = account['page_id']
                    existing.page_name = account['page_name']
                    existing.username = account['instagram_account']['username']
                    logger.info("Updated Instagram account info", extra={"user_id": user_id, "username": account['instagram_account']['username']})
            else:
                logger.info("Creating new Instagram credentials", extra={"user_id": user_id})
                # Create new credentials
                instagram_accounts = token_data.get('instagram_accounts', [])
                account = instagram_accounts[0] if instagram_accounts else {}
                
                credentials = InstagramCredentials(
                    id=f"ig_{user_id}_{datetime.utcnow().timestamp()}",
                    user_id=user_id,
                    access_token=token_data['access_token'],
                    token_type=token_data['token_type'],
                    expires_at=datetime.fromisoformat(token_data['expires_at']),
                    instagram_business_account_id=account.get('instagram_account', {}).get('id'),
                    page_id=account.get('page_id'),
                    page_name=account.get('page_name'),
                    username=account.get('instagram_account', {}).get('username')
                )
                db.add(credentials)
                logger.debug("New credentials object created", extra={"user_id": user_id})
            
            db.commit()
            logger.info("Instagram credentials saved successfully", extra={"user_id": user_id})
            return True
            
        except Exception as e:
            logger.error("Failed to save Instagram credentials", extra={"user_id": user_id, "error": str(e)}, exc_info=True)
            return False
        finally:
            logger.debug("Closing database session", extra={"user_id": user_id})
            db.close()
    
    def get_credentials(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get Instagram credentials for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Credentials dict or None if not found
        """
        try:
            db = SessionLocal()
            credentials = db.query(InstagramCredentials).filter(
                InstagramCredentials.user_id == user_id
            ).first()
            
            if credentials:
                return {
                    'access_token': credentials.access_token,
                    'instagram_business_account_id': credentials.instagram_business_account_id,
                    'page_id': credentials.page_id,
                    'page_name': credentials.page_name,
                    'username': credentials.username,
                    'token_type': credentials.token_type,
                    'expires_at': credentials.expires_at.isoformat() if credentials.expires_at else None,
                    'created_at': credentials.created_at.isoformat(),
                    'updated_at': credentials.updated_at.isoformat()
                }
            return None
            
        except Exception as e:
            logger.error("Failed to get Instagram credentials", extra={"user_id": user_id, "error": str(e)})
            return None
        finally:
            db.close()
    
    def delete_credentials(self, user_id: str) -> bool:
        """
        Delete Instagram credentials for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            True if deleted successfully
        """
        try:
            db = SessionLocal()
            credentials = db.query(InstagramCredentials).filter(
                InstagramCredentials.user_id == user_id
            ).first()
            
            if credentials:
                db.delete(credentials)
                db.commit()
                return True
            return False
            
        except Exception as e:
            logger.error("Failed to delete Instagram credentials", extra={"user_id": user_id, "error": str(e)})
            return False
        finally:
            db.close()
    
    def is_token_valid(self, user_id: str) -> bool:
        """
        Check if the stored token is still valid
        
        Args:
            user_id: User identifier
            
        Returns:
            True if token exists and is not expired
        """
        try:
            logger.debug("Checking Instagram token validity", extra={"user_id": user_id})
            db = SessionLocal()
            credentials = db.query(InstagramCredentials).filter(
                InstagramCredentials.user_id == user_id
            ).first()
            
            if not credentials:
                logger.warning("No Instagram credentials found", extra={"user_id": user_id})
                return False
            
            logger.debug("Found Instagram credentials", extra={"user_id": user_id, "expires_at": credentials.expires_at, "current_time": datetime.utcnow()})
            
            # Check if token is expired
            if credentials.expires_at and credentials.expires_at < datetime.utcnow():
                logger.warning("Instagram token is expired", extra={"user_id": user_id})
                return False
            
            logger.debug("Instagram token is valid", extra={"user_id": user_id})
            return True
            
        except Exception as e:
            logger.error("Failed to check Instagram token validity", extra={"user_id": user_id, "error": str(e)})
            return False
        finally:
            db.close()
    
    def get_access_token(self, user_id: str) -> Optional[str]:
        """
        Get the access token for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Access token or None if not found/expired
        """
        logger.debug("Getting Instagram access token", extra={"user_id": user_id})
        
        if not self.is_token_valid(user_id):
            logger.warning("Instagram token is not valid", extra={"user_id": user_id})
            return None
        
        credentials = self.get_credentials(user_id)
        if credentials:
            logger.debug("Found Instagram credentials", extra={"user_id": user_id, "token_preview": credentials['access_token'][:20] + "..."})
            return credentials['access_token']
        else:
            logger.warning("No Instagram credentials found", extra={"user_id": user_id})
            return None
    
    def should_refresh_token(self, user_id: str) -> bool:
        """
        Check if token should be refreshed (expires within 7 days)
        
        Args:
            user_id: User identifier
            
        Returns:
            True if token should be refreshed
        """
        try:
            db = SessionLocal()
            credentials = db.query(InstagramCredentials).filter(
                InstagramCredentials.user_id == user_id
            ).first()
            
            if not credentials or not credentials.expires_at:
                return False
            
            # Check if token expires within 7 days
            seven_days_from_now = datetime.utcnow() + timedelta(days=7)
            return credentials.expires_at < seven_days_from_now
            
        except Exception as e:
            logger.error("Failed to check if Instagram token should be refreshed", extra={"user_id": user_id, "error": str(e)})
            return False
        finally:
            db.close()


# Global instance
instagram_credentials_service = InstagramCredentialsService()
