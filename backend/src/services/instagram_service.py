import os
import requests
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstagramService:
    """Service for posting to Instagram using Instagram Graph API"""
    
    def __init__(self, access_token: str, instagram_business_account_id: str = None):
        """
        Initialize Instagram service
        
        Args:
            access_token: Facebook/Instagram access token
            instagram_business_account_id: Instagram Business Account ID (optional, will be fetched if not provided)
        """
        self.access_token = access_token
        self.instagram_business_account_id = instagram_business_account_id
        self.base_url = "https://graph.facebook.com/v18.0"
        
        # Validate access token
        if not self._validate_access_token():
            raise ValueError("Invalid access token or insufficient permissions")
        
        # Get Instagram Business Account ID if not provided
        if not self.instagram_business_account_id:
            self.instagram_business_account_id = self._get_instagram_business_account_id()
    
    def _validate_access_token(self) -> bool:
        """Validate the access token and check permissions"""
        try:
            url = f"{self.base_url}/me"
            params = {
                'access_token': self.access_token,
                'fields': 'id,name,accounts'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Access token validated for user: {data.get('name', 'Unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Access token validation failed: {e}")
            return False
    
    def _get_instagram_business_account_id(self) -> str:
        """Get Instagram Business Account ID from Facebook pages"""
        try:
            url = f"{self.base_url}/me/accounts"
            params = {
                'access_token': self.access_token,
                'fields': 'id,name,instagram_business_account'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            pages = data.get('data', [])
            
            for page in pages:
                if page.get('instagram_business_account'):
                    instagram_id = page['instagram_business_account']['id']
                    logger.info(f"Found Instagram Business Account ID: {instagram_id}")
                    return instagram_id
            
            raise ValueError("No Instagram Business Account found. Please ensure your Facebook page is connected to Instagram.")
            
        except Exception as e:
            logger.error(f"Failed to get Instagram Business Account ID: {e}")
            raise
    
    def create_media_container(self, caption: str, media_type: str = "CAROUSEL_ALBUM") -> Dict[str, Any]:
        """
        Create a media container for Instagram post
        
        Args:
            caption: Post caption text
            media_type: Type of media (CAROUSEL_ALBUM, IMAGE, VIDEO)
        
        Returns:
            Response data from Instagram API
        """
        try:
            url = f"{self.base_url}/{self.instagram_business_account_id}/media"
            
            data = {
                'access_token': self.access_token,
                'caption': caption,
                'media_type': media_type
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Media container created: {result.get('id')}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create media container: {e}")
            raise
    
    def publish_media(self, creation_id: str) -> Dict[str, Any]:
        """
        Publish the created media container
        
        Args:
            creation_id: ID returned from create_media_container
        
        Returns:
            Response data from Instagram API
        """
        try:
            url = f"{self.base_url}/{self.instagram_business_account_id}/media_publish"
            
            data = {
                'access_token': self.access_token,
                'creation_id': creation_id
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Media published successfully: {result.get('id')}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to publish media: {e}")
            raise
    
    def post_text_only(self, caption: str) -> Dict[str, Any]:
        """
        Post text-only content to Instagram
        
        Args:
            caption: Post caption text
        
        Returns:
            Response data from Instagram API
        """
        try:
            # Instagram requires at least one media item, so we'll create a simple text post
            # using a placeholder image or text overlay
            
            # For now, we'll create a media container with text
            media_result = self.create_media_container(caption, "IMAGE")
            creation_id = media_result.get('id')
            
            if creation_id:
                # Publish the media
                publish_result = self.publish_media(creation_id)
                
                return {
                    'status': 'success',
                    'instagram_post_id': publish_result.get('id'),
                    'creation_id': creation_id,
                    'caption': caption,
                    'posted_at': datetime.now().isoformat(),
                    'api_response': publish_result
                }
            else:
                raise ValueError("Failed to create media container")
                
        except Exception as e:
            logger.error(f"Failed to post text-only content: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'posted_at': datetime.now().isoformat()
            }
    
    def post_with_image(self, caption: str, image_url: str) -> Dict[str, Any]:
        """
        Post image with caption to Instagram
        
        Args:
            caption: Post caption text
            image_url: URL of the image to post
        
        Returns:
            Response data from Instagram API
        """
        try:
            # First, upload the image to get a media ID
            # This is a simplified version - in production you'd need to handle image uploads properly
            
            url = f"{self.base_url}/{self.instagram_business_account_id}/media"
            
            data = {
                'access_token': self.access_token,
                'caption': caption,
                'media_type': 'IMAGE',
                'image_url': image_url
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            media_result = response.json()
            creation_id = media_result.get('id')
            
            if creation_id:
                # Publish the media
                publish_result = self.publish_media(creation_id)
                
                return {
                    'status': 'success',
                    'instagram_post_id': publish_result.get('id'),
                    'creation_id': creation_id,
                    'caption': caption,
                    'image_url': image_url,
                    'posted_at': datetime.now().isoformat(),
                    'api_response': publish_result
                }
            else:
                raise ValueError("Failed to create media container with image")
                
        except Exception as e:
            logger.error(f"Failed to post with image: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'posted_at': datetime.now().isoformat()
            }
    
    def get_post_status(self, post_id: str) -> Dict[str, Any]:
        """
        Get the status of a posted media
        
        Args:
            post_id: Instagram post ID
        
        Returns:
            Response data from Instagram API
        """
        try:
            url = f"{self.base_url}/{post_id}"
            params = {
                'access_token': self.access_token,
                'fields': 'id,media_type,media_url,thumbnail_url,permalink,timestamp'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get post status: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def delete_post(self, post_id: str) -> bool:
        """
        Delete a posted media (if supported by the API)
        
        Args:
            post_id: Instagram post ID
        
        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}/{post_id}"
            params = {'access_token': self.access_token}
            
            response = requests.delete(url, params=params)
            response.raise_for_status()
            
            logger.info(f"Post {post_id} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete post {post_id}: {e}")
            return False
