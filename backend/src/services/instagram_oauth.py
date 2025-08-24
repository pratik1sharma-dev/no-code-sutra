import os
import requests
import json
import secrets
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from urllib.parse import urlencode, parse_qs, urlparse
import logging

logger = logging.getLogger(__name__)

class InstagramOAuthService:
    """OAuth 2.0 service for Instagram/Facebook authentication"""
    
    def __init__(self):
        self.app_id = os.getenv('FACEBOOK_APP_ID')
        self.app_secret = os.getenv('FACEBOOK_APP_SECRET')
        self.redirect_uri = os.getenv('INSTAGRAM_REDIRECT_URI', 'http://localhost:8000/api/auth/instagram/callback')
        self.base_url = "https://graph.facebook.com/v23.0"
        
        print(f"🔍 Instagram OAuth Service initialized with redirect_uri: {self.redirect_uri}")
        
        if not self.app_id or not self.app_secret:
            raise ValueError("FACEBOOK_APP_ID and FACEBOOK_APP_SECRET must be set in environment variables")
    
    def get_authorization_url(self, state: str = None) -> str:
        """
        Generate Instagram authorization URL for OAuth flow
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Authorization URL for user to visit
        """
        if not state:
            state = secrets.token_urlsafe(32)
        
        params = {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'pages_show_list,business_management,instagram_basic,instagram_manage_insights,instagram_content_publish,pages_read_engagement',
            'response_type': 'code',
            'state': state
        }
        
        auth_url = f"https://www.facebook.com/v23.0/dialog/oauth?{urlencode(params)}"
        logger.info(f"Generated authorization URL with state: {state}")
        print(f"🔍 Generated auth URL with redirect_uri: {self.redirect_uri}")
        return auth_url
    
    def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        
        Args:
            authorization_code: Code received from Instagram OAuth callback
            
        Returns:
            Token response with access_token, token_type, expires_in, etc.
        """
        try:
            url = f"{self.base_url}/oauth/access_token"
            params = {
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'redirect_uri': self.redirect_uri,
                'code': authorization_code
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            token_data = response.json()
            logger.info("Successfully exchanged authorization code for access token")
            return token_data
            
        except Exception as e:
            logger.error(f"Failed to exchange code for token: {e}")
            raise
    
    def get_long_lived_token(self, short_lived_token: str) -> Dict[str, Any]:
        """
        Exchange short-lived token for long-lived token (60 days)
        
        Args:
            short_lived_token: Short-lived access token
            
        Returns:
            Long-lived token response
        """
        try:
            url = f"{self.base_url}/oauth/access_token"
            params = {
                'grant_type': 'fb_exchange_token',
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'fb_exchange_token': short_lived_token
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            token_data = response.json()
            logger.info("Successfully exchanged for long-lived token")
            return token_data
            
        except Exception as e:
            logger.error(f"Failed to get long-lived token: {e}")
            raise
    
    def refresh_long_lived_token(self, long_lived_token: str) -> Dict[str, Any]:
        """
        Refresh a long-lived token before it expires
        
        Args:
            long_lived_token: Current long-lived token
            
        Returns:
            New long-lived token response
        """
        try:
            url = f"{self.base_url}/oauth/access_token"
            params = {
                'grant_type': 'fb_exchange_token',
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'fb_exchange_token': long_lived_token
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            token_data = response.json()
            logger.info("Successfully refreshed long-lived token")
            return token_data
            
        except Exception as e:
            logger.error(f"Failed to refresh long-lived token: {e}")
            raise
    
    def validate_token(self, access_token: str) -> Dict[str, Any]:
        """
        Validate access token and get user information
        
        Args:
            access_token: Access token to validate
            
        Returns:
            Token validation response with user info and permissions
        """
        try:
            url = f"{self.base_url}/me"
            params = {
                'access_token': access_token,
                'fields': 'id,name,email'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            user_data = response.json()
            
            # Get permissions
            permissions_url = f"{self.base_url}/me/permissions"
            permissions_response = requests.get(permissions_url, params={'access_token': access_token})
            permissions_data = permissions_response.json()
            
            result = {
                'valid': True,
                'user': user_data,
                'permissions': permissions_data.get('data', []),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Token validated for user: {user_data.get('name', 'Unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return {
                'valid': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_instagram_accounts(self, access_token: str) -> List[Dict[str, Any]]:
        """
        Get Instagram Business Accounts associated with the user
        
        Args:
            access_token: Valid access token
            
        Returns:
            List of Instagram Business Accounts
        """
        try:
            url = f"{self.base_url}/me/accounts"
            params = {
                'access_token': access_token,
                'fields': 'id,name,instagram_business_account{id,username,name,profile_picture_url}'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            pages = data.get('data', [])
            
            instagram_accounts = []
            for page in pages:
                if page.get('instagram_business_account'):
                    instagram_accounts.append({
                        'page_id': page['id'],
                        'page_name': page['name'],
                        'instagram_account': page['instagram_business_account']
                    })
            
            logger.info(f"Found {len(instagram_accounts)} Instagram Business Accounts")
            return instagram_accounts
            
        except Exception as e:
            logger.error(f"Failed to get Instagram accounts: {e}")
            raise
    
    def complete_oauth_flow(self, authorization_code: str) -> Dict[str, Any]:
        """
        Complete the full OAuth flow: code -> short token -> long token
        
        Args:
            authorization_code: Authorization code from callback
            
        Returns:
            Complete token information with Instagram accounts
        """
        try:
            # Step 1: Exchange code for short-lived token
            short_token_data = self.exchange_code_for_token(authorization_code)
            short_lived_token = short_token_data['access_token']
            
            # Step 2: Exchange for long-lived token
            long_token_data = self.get_long_lived_token(short_lived_token)
            long_lived_token = long_token_data['access_token']
            
            # Step 3: Get Instagram accounts
            instagram_accounts = self.get_instagram_accounts(long_lived_token)
            
            # Step 4: Validate token
            validation = self.validate_token(long_lived_token)
            
            result = {
                'access_token': long_lived_token,
                'token_type': 'long_lived',
                'expires_in': long_token_data.get('expires_in', 5184000),  # 60 days in seconds
                'expires_at': (datetime.now() + timedelta(seconds=long_token_data.get('expires_in', 5184000))).isoformat(),
                'instagram_accounts': instagram_accounts,
                'validation': validation,
                'created_at': datetime.now().isoformat()
            }
            
            logger.info("OAuth flow completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"OAuth flow failed: {e}")
            raise
