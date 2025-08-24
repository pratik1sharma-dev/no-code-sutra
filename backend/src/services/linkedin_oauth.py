import os
import requests
import secrets
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from urllib.parse import urlencode
import logging

logger = logging.getLogger(__name__)


class LinkedInOAuthService:
	"""OAuth 2.0 service for LinkedIn authentication"""

	def __init__(self):
		self.client_id = os.getenv('LINKEDIN_CLIENT_ID')
		self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
		self.redirect_uri = os.getenv('LINKEDIN_REDIRECT_URI', 'http://localhost:8000/api/auth/linkedin/callback')
		self.auth_base = 'https://www.linkedin.com/oauth/v2'
		self.api_base = 'https://api.linkedin.com/v2'
		if not self.client_id or not self.client_secret:
			raise ValueError("LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET must be set in environment variables")

	def get_authorization_url(self, state: Optional[str] = None) -> str:
		"""Generate LinkedIn authorization URL for OAuth flow"""
		if not state:
			state = secrets.token_urlsafe(32)
		scopes = [
			'r_liteprofile',
			'r_emailaddress',
			'w_member_social',
			'offline_access'
		]
		params = {
			'response_type': 'code',
			'client_id': self.client_id,
			'redirect_uri': self.redirect_uri,
			'state': state,
			'scope': ' '.join(scopes)
		}
		url = f"{self.auth_base}/authorization?{urlencode(params)}"
		logger.info(f"Generated LinkedIn authorization URL with state: {state}")
		print(f"🔍 LinkedIn OAuth auth URL generated with redirect_uri: {self.redirect_uri}")
		return url

	def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
		"""Exchange authorization code for access (and refresh) token"""
		url = f"{self.auth_base}/accessToken"
		data = {
			'grant_type': 'authorization_code',
			'code': authorization_code,
			'redirect_uri': self.redirect_uri,
			'client_id': self.client_id,
			'client_secret': self.client_secret,
		}
		response = requests.post(url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
		response.raise_for_status()
		return response.json()

	def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
		"""Refresh access token using refresh token (requires offline_access scope)"""
		url = f"{self.auth_base}/accessToken"
		data = {
			'grant_type': 'refresh_token',
			'refresh_token': refresh_token,
			'client_id': self.client_id,
			'client_secret': self.client_secret,
		}
		response = requests.post(url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
		response.raise_for_status()
		return response.json()

	def _get_headers(self, access_token: str) -> Dict[str, str]:
		return {
			'Authorization': f'Bearer {access_token}',
			'X-Restli-Protocol-Version': '2.0.0',
		}

	def get_user_profile(self, access_token: str) -> Dict[str, Any]:
		"""Fetch user profile to derive author URN"""
		url = f"{self.api_base}/me"
		resp = requests.get(url, headers=self._get_headers(access_token))
		resp.raise_for_status()
		return resp.json()

	def validate_token(self, access_token: str) -> Dict[str, Any]:
		"""Basic validation by calling /me; returns profile data if valid"""
		try:
			profile = self.get_user_profile(access_token)
			return {
				'valid': True,
				'user': profile
			}
		except Exception as e:
			logger.error(f"LinkedIn token validation failed: {e}")
			return {
				'valid': False,
				'error': str(e)
			}

	def complete_oauth_flow(self, authorization_code: str) -> Dict[str, Any]:
		"""Complete OAuth: code -> token -> profile"""
		token_data = self.exchange_code_for_token(authorization_code)
		access_token = token_data.get('access_token')
		refresh_token = token_data.get('refresh_token')
		expires_in = token_data.get('expires_in')
		profile = self.get_user_profile(access_token)
		author_urn = profile.get('id')
		if author_urn and not author_urn.startswith('urn:'):
			author_urn = f"urn:li:person:{author_urn}"
		return {
			'access_token': access_token,
			'refresh_token': refresh_token,
			'expires_in': expires_in,
			'expires_at': (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat() if expires_in else None,
			'scopes': token_data.get('scope') or token_data.get('scopes'),
			'author_urn': author_urn,
			'metadata': {
				'profile': profile
			}
		}

