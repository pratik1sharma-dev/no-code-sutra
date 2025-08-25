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
        self.base_url = "https://graph.facebook.com/v23.0"
        
        # Validate access token
        if not self._validate_access_token():
            raise ValueError("Invalid access token or insufficient permissions")
        
        # Get Instagram Business Account ID if not provided
        if not self.instagram_business_account_id:
            self.instagram_business_account_id = self._get_instagram_business_account_id()
    
    def _validate_access_token(self) -> bool:
        """Validate the access token and check permissions"""
        try:
            print(f"🔍 Validating access token: {self.access_token[:20]}...")
            url = f"{self.base_url}/me"
            params = {
                'access_token': self.access_token,
                'fields': 'id,name'
            }
            
            print(f"🔍 Making validation request to: {url}")
            response = requests.get(url, params=params)
            print(f"🔍 Response status: {response.status_code}")
            print(f"🔍 Response content: {response.text[:200]}...")
            
            response.raise_for_status()
            
            data = response.json()
            print(f"🔍 ✅ Access token validated for user: {data.get('name', 'Unknown')}")
            logger.info(f"Access token validated for user: {data.get('name', 'Unknown')}")
            return True
            
        except Exception as e:
            print(f"🔍 ❌ Access token validation failed: {e}")
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
    
    def _truncate_caption(self, caption: str, max_length: int = 2200) -> str:
        """
        Truncate caption to Instagram's maximum length
        
        Args:
            caption: Original caption text
            max_length: Maximum allowed length (Instagram limit is 2200)
        
        Returns:
            Truncated caption
        """
        if len(caption) <= max_length:
            return caption
        
        # Truncate and add ellipsis
        truncated = caption[:max_length-3] + "..."
        logger.warning(f"Caption truncated from {len(caption)} to {len(truncated)} characters")
        return truncated
    
    def create_media_container(self, caption: str, media_type: str = "IMAGE", image_url: str = None) -> Dict[str, Any]:
        """
        Create a media container for Instagram post
        
        Args:
            caption: Post caption text
            media_type: Type of media (CAROUSEL_ALBUM, IMAGE, VIDEO)
            image_url: URL of the image (required for IMAGE type)
        
        Returns:
            Response data from Instagram API
        """
        try:
            # Truncate caption if it exceeds Instagram's limit
            truncated_caption = self._truncate_caption(caption)
            
            url = f"{self.base_url}/{self.instagram_business_account_id}/media"
            
            data = {
                'access_token': self.access_token,
                'caption': truncated_caption,
                'media_type': media_type
            }
            
            # Add image_url if provided
            if image_url:
                data['image_url'] = image_url
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Media container created: {result.get('id')}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create media container: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
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
    
    def post_text_only(self, caption: str, image_url: str = None) -> Dict[str, Any]:
        """
        Post text-only content to Instagram
        
        Args:
            caption: Post caption text
            image_url: Optional image URL (required since Instagram needs media)
        
        Returns:
            Response data from Instagram API
        """
        try:
            print(f"🔍 Instagram Service: Starting post_text_only")
            print(f"🔍 Caption length: {len(caption)}")
            print(f"🔍 Image URL: {image_url}")
            print(f"🔍 Instagram Business Account ID: {self.instagram_business_account_id}")
            
            # Instagram requires at least one media item
            if not image_url:
                print(f"🔍 ❌ No image URL provided - Instagram requires media")
                return {
                    'status': 'failed',
                    'error': 'Instagram requires media for posts. Please provide an image_url parameter.',
                    'posted_at': datetime.now().isoformat()
                }
            
            # Create a media container with the provided image
            print(f"🔍 Creating media container...")
            media_result = self.create_media_container(caption, "IMAGE", image_url)
            creation_id = media_result.get('id')
            print(f"🔍 Media container result: {media_result}")
            print(f"🔍 Creation ID: {creation_id}")
            
            if creation_id:
                # Publish the media
                print(f"🔍 Publishing media with creation ID: {creation_id}")
                publish_result = self.publish_media(creation_id)
                print(f"🔍 Publish result: {publish_result}")
                
                # Truncate caption for response
                truncated_caption = self._truncate_caption(caption)
                
                return {
                    'status': 'success',
                    'instagram_post_id': publish_result.get('id'),
                    'creation_id': creation_id,
                    'caption': truncated_caption,
                    'original_caption_length': len(caption),
                    'posted_at': datetime.now().isoformat(),
                    'api_response': publish_result
                }
            else:
                raise ValueError("Failed to create media container")
                
        except Exception as e:
            print(f"🔍 ❌ Instagram post_text_only failed: {e}")
            logger.error(f"Failed to post text-only content: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"🔍 Response content: {e.response.text}")
                logger.error(f"Response content: {e.response.text}")
            import traceback
            traceback.print_exc()
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
            # Truncate caption if it exceeds Instagram's limit
            truncated_caption = self._truncate_caption(caption)
            
            url = f"{self.base_url}/{self.instagram_business_account_id}/media"
            
            data = {
                'access_token': self.access_token,
                'caption': truncated_caption,
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
                    'caption': truncated_caption,
                    'original_caption_length': len(caption),
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

    def post_carousel(self, caption: str, image_urls: List[str]) -> Dict[str, Any]:
        """
        Post carousel (multiple images) to Instagram
        
        Args:
            caption: Post caption text
            image_urls: List of image URLs for the carousel (2-10 images)
        
        Returns:
            Response data from Instagram API
        """
        try:
            print(f"🔍 Instagram Service: Starting post_carousel")
            print(f"🔍 Caption length: {len(caption)}")
            print(f"🔍 Number of images: {len(image_urls)}")
            print(f"🔍 Image URLs: {image_urls}")
            
            # Validate input
            if not image_urls or len(image_urls) < 2:
                return {
                    'status': 'failed',
                    'error': 'Carousel requires at least 2 images',
                    'posted_at': datetime.now().isoformat()
                }
            
            if len(image_urls) > 10:
                return {
                    'status': 'failed',
                    'error': 'Carousel cannot have more than 10 images',
                    'posted_at': datetime.now().isoformat()
                }
            
            # Truncate caption if it exceeds Instagram's limit
            truncated_caption = self._truncate_caption(caption)
            
            url = f"{self.base_url}/{self.instagram_business_account_id}/media"
            
            # Step 1: Create child media objects (upload each image as carousel item)
            print(f"🔍 Creating child media objects for {len(image_urls)} images...")
            media_ids = []
            
            for i, image_url in enumerate(image_urls):
                print(f"🔍 Uploading image {i+1}/{len(image_urls)}...")
                
                # Create child media object with is_carousel_item=true
                child_data = {
                    'access_token': self.access_token,
                    'image_url': image_url,
                    'is_carousel_item': 'true'
                }
                
                response = requests.post(url, data=child_data)
                response.raise_for_status()
                
                child_result = response.json()
                child_id = child_result.get('id')
                
                if child_id:
                    media_ids.append(child_id)
                    print(f"✅ Image {i+1} uploaded")
                else:
                    raise ValueError(f"Failed to upload image {i+1}")
            
            print(f"🔍 All {len(media_ids)} images uploaded successfully")
            
            # Wait for child media objects to be ready
            print(f"🔍 Waiting for child media objects to be ready...")
            import time
            
            for i, media_id in enumerate(media_ids):
                max_retries = 10
                for attempt in range(max_retries):
                    status_url = f"{self.base_url}/{media_id}"
                    status_params = {'access_token': self.access_token, 'fields': 'status_code'}
                    
                    status_response = requests.get(status_url, params=status_params)
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        status_code = status_data.get('status_code')
                        
                        if status_code == 'FINISHED':
                            print(f"✅ Image {i+1} ready")
                            break
                        elif status_code == 'ERROR':
                            raise ValueError(f"Image {i+1} failed")
                        else:
                            time.sleep(2)
                    else:
                        time.sleep(2)
                else:
                    raise ValueError(f"Image {i+1} not ready after {max_retries} attempts")
            
            # Step 2: Create carousel container
            print(f"🔍 Creating carousel container...")
            
            carousel_data = {
                'access_token': self.access_token,
                'media_type': 'CAROUSEL',
                'caption': truncated_caption,
                'children': json.dumps(media_ids)
            }
            
            print(f"🔍 Creating carousel with {len(media_ids)} images...")
            
            response = requests.post(url, data=carousel_data)
            response.raise_for_status()
            
            carousel_result = response.json()
            creation_id = carousel_result.get('id')
            print(f"🔍 Carousel media container result: {carousel_result}")
            print(f"🔍 Creation ID: {creation_id}")
            
            if creation_id:
                # Publish the carousel
                print(f"🔍 Publishing carousel with creation ID: {creation_id}")
                publish_result = self.publish_media(creation_id)
                print(f"🔍 Publish result: {publish_result}")
                
                print(f"✅ Carousel posted successfully! Post ID: {publish_result.get('id')}")
                
                return {
                    'status': 'success',
                    'instagram_post_id': publish_result.get('id'),
                    'creation_id': creation_id,
                    'caption': truncated_caption,
                    'original_caption_length': len(caption),
                    'image_urls': image_urls,
                    'image_count': len(image_urls),
                    'media_ids': media_ids,
                    'posted_at': datetime.now().isoformat(),
                    'api_response': publish_result
                }
            else:
                raise ValueError("Failed to create carousel media container")
                
        except Exception as e:
            print(f"🔍 ❌ Instagram post_carousel failed: {e}")
            logger.error(f"Failed to post carousel: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"🔍 Response content: {e.response.text}")
                logger.error(f"Response content: {e.response.text}")
            import traceback
            traceback.print_exc()
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
