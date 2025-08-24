import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .db import SessionLocal
from .models import LinkedInCredentials


class LinkedInCredentialsService:
	"""Service for managing LinkedIn credentials in the database"""

	def save_credentials(self, user_id: str, token_data: Dict[str, Any]) -> bool:
		"""
		Save LinkedIn credentials to database

		Args:
			user_id: User identifier
			token_data: Token data from OAuth flow

		Returns:
			True if saved successfully
		"""
		try:
			db = SessionLocal()
			existing = db.query(LinkedInCredentials).filter(
				LinkedInCredentials.user_id == user_id
			).first()

			if existing:
				existing.access_token = token_data.get('access_token')
				existing.refresh_token = token_data.get('refresh_token')
				existing.scopes = ' '.join(token_data.get('scopes', [])) if isinstance(token_data.get('scopes'), list) else token_data.get('scopes')
				existing.expires_at = datetime.fromisoformat(token_data['expires_at']) if token_data.get('expires_at') else None
				existing.author_urn = token_data.get('author_urn')
				existing.metadata = token_data.get('metadata')
				existing.updated_at = datetime.utcnow()
			else:
				credentials = LinkedInCredentials(
					id=f"li_{user_id}_{datetime.utcnow().timestamp()}",
					user_id=user_id,
					access_token=token_data.get('access_token'),
					refresh_token=token_data.get('refresh_token'),
					scopes=' '.join(token_data.get('scopes', [])) if isinstance(token_data.get('scopes'), list) else token_data.get('scopes'),
					expires_at=datetime.fromisoformat(token_data['expires_at']) if token_data.get('expires_at') else None,
					author_urn=token_data.get('author_urn'),
					metadata=token_data.get('metadata')
				)
				db.add(credentials)

			db.commit()
			return True
		except Exception as e:
			print(f"Error saving LinkedIn credentials: {e}")
			return False
		finally:
			db.close()

	def get_credentials(self, user_id: str) -> Optional[Dict[str, Any]]:
		"""Get LinkedIn credentials for a user"""
		try:
			db = SessionLocal()
			credentials = db.query(LinkedInCredentials).filter(
				LinkedInCredentials.user_id == user_id
			).first()
			if credentials:
				return {
					'access_token': credentials.access_token,
					'refresh_token': credentials.refresh_token,
					'scopes': credentials.scopes,
					'expires_at': credentials.expires_at.isoformat() if credentials.expires_at else None,
					'author_urn': credentials.author_urn,
					'metadata': credentials.metadata,
					'created_at': credentials.created_at.isoformat(),
					'updated_at': credentials.updated_at.isoformat()
				}
			return None
		except Exception as e:
			print(f"Error getting LinkedIn credentials: {e}")
			return None
		finally:
			db.close()

	def delete_credentials(self, user_id: str) -> bool:
		"""Delete LinkedIn credentials for a user"""
		try:
			db = SessionLocal()
			credentials = db.query(LinkedInCredentials).filter(
				LinkedInCredentials.user_id == user_id
			).first()
			if credentials:
				db.delete(credentials)
				db.commit()
				return True
			return False
		except Exception as e:
			print(f"Error deleting LinkedIn credentials: {e}")
			return False
		finally:
			db.close()

	def is_token_valid(self, user_id: str) -> bool:
		"""Check if the stored token exists and is not expired"""
		try:
			db = SessionLocal()
			credentials = db.query(LinkedInCredentials).filter(
				LinkedInCredentials.user_id == user_id
			).first()
			if not credentials:
				return False
			if credentials.expires_at and credentials.expires_at < datetime.utcnow():
				return False
			return True
		except Exception as e:
			print(f"Error checking LinkedIn token validity: {e}")
			return False
		finally:
			db.close()

	def get_access_token(self, user_id: str) -> Optional[str]:
		"""Get a valid access token if available"""
		if not self.is_token_valid(user_id):
			return None
		creds = self.get_credentials(user_id)
		return creds.get('access_token') if creds else None


# Global instance
linkedin_credentials_service = LinkedInCredentialsService()

