import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .db import SessionLocal
from .models import InstagramCredentials


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

            print(f"🔍 Saving credentials for user: {user_id}")
            print(f"🔍 Token data keys: {list(token_data.keys())}")
            
            db = SessionLocal()
            print("🔍 Database session created")
            
            # Check if credentials already exist for this user
            existing = db.query(InstagramCredentials).filter(
                InstagramCredentials.user_id == user_id
            ).first()
            
            print(f"🔍 Existing credentials found: {existing is not None}")
            
            if existing:
                print("🔍 Updating existing credentials")
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
                    print(f"🔍 Updated Instagram account: {account['instagram_account']['username']}")
            else:
                print("🔍 Creating new credentials")
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
                print(f"🔍 New credentials object created")
            
            print("🔍 Committing to database...")
            db.commit()
            print("🔍 Database commit successful")
            return True
            
        except Exception as e:
            print(f"❌ Error saving Instagram credentials: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            print("🔍 Closing database session")
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
            print(f"Error getting Instagram credentials: {e}")
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
            print(f"Error deleting Instagram credentials: {e}")
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
            print(f"🔍 Checking token validity for user: {user_id}")
            db = SessionLocal()
            credentials = db.query(InstagramCredentials).filter(
                InstagramCredentials.user_id == user_id
            ).first()
            
            if not credentials:
                print(f"🔍 ❌ No credentials found for user: {user_id}")
                return False
            
            print(f"🔍 Found credentials, expires at: {credentials.expires_at}")
            print(f"🔍 Current time: {datetime.utcnow()}")
            
            # Check if token is expired
            if credentials.expires_at and credentials.expires_at < datetime.utcnow():
                print(f"🔍 ❌ Token is expired")
                return False
            
            print(f"🔍 ✅ Token is valid")
            return True
            
        except Exception as e:
            print(f"🔍 ❌ Error checking token validity: {e}")
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
        print(f"🔍 Getting access token for user: {user_id}")
        
        if not self.is_token_valid(user_id):
            print(f"🔍 ❌ Token is not valid for user: {user_id}")
            return None
        
        credentials = self.get_credentials(user_id)
        if credentials:
            print(f"🔍 ✅ Found credentials for user: {user_id}")
            print(f"🔍 Token preview: {credentials['access_token'][:20]}...")
            return credentials['access_token']
        else:
            print(f"🔍 ❌ No credentials found for user: {user_id}")
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
            print(f"Error checking if token should be refreshed: {e}")
            return False
        finally:
            db.close()


# Global instance
instagram_credentials_service = InstagramCredentialsService()
