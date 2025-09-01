import json
import os
from typing import Dict, Any
from datetime import datetime

from ..instagram_service import InstagramService
from ..instagram_credentials import instagram_credentials_service


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        platform = state.get('platform', 'instagram')
        content = state.get('content', '')
        access_token = state.get('access_token', '')
        post = state.get('post', '')
        image_url = state.get('image_url', '')
        image = state.get('image', '')
        user_id = state.get('user_id', 'default_user')  # Default user ID for demo
        post_type = state.get('post_type', 'single')  # Get post type
        
        print(f"🔍 SOCIAL MEDIA NODE DEBUG: Platform={platform}, PostType={post_type}")
        print(f"🔍 Content: {content}")
        
        if platform == 'instagram' or platform == 'instagram_post':
            # Get content, prioritizing the 'dynamic' key from aiAgent
            if 'dynamic' in state and state['dynamic']:
                content = state['dynamic']
                print(f"🔍 Using content from 'dynamic' key.")
            elif 'structured_data' in state and state['structured_data']:
                content = state['structured_data']
                print(f"🔍 Using structured_data: {content}")
            elif not content:
                for key in ['post_data', 'output_data', 'result', 'output', 'content', 'text']:
                    if key in state and state[key]:
                        content = state[key]
                        break
            if not content and post:
                if isinstance(post, str) and '.' in post:
                    parts = post.split('.')
                    if len(parts) == 2 and parts[1] in state:
                        content = state[parts[1]]
                    else:
                        content = post
                else:
                    content = post
                    
            # Handle image URLs - prioritize text overlay images, fallback to regenerating overlay
            if not image_url:
                # Check for text overlay image first (this is the final image with text)
                if 'image_data_url' in state and state['image_data_url']:
                    image_url = state['image_data_url']
                    print(f"🔍 Using text overlay image: {image_url[:50]}...")
                elif image:
                    if isinstance(image, dict) and 'image_url' in image:
                        image_url = image.get('image_url')
                    elif isinstance(image, str):
                        image_url = image
                elif 'background_image_url' in state:
                    image_url = state['background_image_url']
                    print(f"🔍 Using background image: {image_url[:50]}...")
                    
                    
            print(f"🔍 Content type: {type(content)}")
            
            if isinstance(content, dict):
                print(f"🔍 Content is a dict with keys: {list(content.keys())}")
                caption = content.get('caption', '')
                hashtags = content.get('hashtags', [])
                summary = content.get('summary', '')
                title = content.get('title', '')
                points = content.get('points', [])
                
                # Handle structured blog data format
                if title and points and not caption:
                    # Create Instagram caption from blog title and points
                    caption = f"{title}\n\n"
                    for i, point_data in enumerate(points[:3], 1):  # Limit to first 3 points
                        if isinstance(point_data, dict):
                            point_text = point_data.get('point', '')
                        else:
                            point_text = str(point_data)
                        if point_text:
                            caption += f"{i}. {point_text[:100]}{'...' if len(point_text) > 100 else ''}\n\n"
                    
                    # Add relevant hashtags
                    caption += "#AI #Technology #Innovation #TechTrends #ArtificialIntelligence"
                
                # Use summary if no caption
                elif not caption and summary:
                    caption = summary[:200] + "..." if len(summary) > 200 else summary
                
                if hashtags and not title:  # Don't add hashtags if we already added them above
                    hashtag_text = ' '.join([f"#{tag.replace('#', '')}" for tag in hashtags])
                    content = f"{caption}\n\n{hashtag_text}"
                else:
                    content = caption
                
                print(f"🔍 Processed content: {content[:100]}...")
                print(f"🔍 Content length: {len(content)}")

            if not content:
                state['status'] = 'failed'
                state['error'] = 'No content available for Instagram post'
                state['timestamp'] = datetime.now().isoformat()
                return state
            print(f"🔍 SOCIAL MEDIA NODE DEBUG: {content}")
            
            # Try to get stored credentials if no access token provided
            print(f"🔍 Checking for stored Instagram credentials for user: {user_id}")
            if not access_token or access_token == 'test_token_12345':
                stored_token = instagram_credentials_service.get_access_token(user_id)
                if stored_token:
                    access_token = stored_token
                    print(f"🔍 ✅ Using stored Instagram token for user: {user_id}")
                    print(f"🔍 Token preview: {stored_token[:20]}...")
                else:
                    print(f"🔍 ❌ No stored Instagram credentials found for user: {user_id}")
            else:
                print(f"🔍 Using provided access token: {access_token[:20]}...")
            
            if access_token and access_token != 'test_token_12345':
                print(f"🔍 Attempting to post to Instagram...")
                print(f"🔍 Content length: {len(str(content))}")
                print(f"🔍 Image URL: {image_url}")
                print(f"🔍 Post Type: {post_type}")
                
                try:
                    print(f"🔍 Creating Instagram service...")
                    instagram_service = InstagramService(access_token)
                    print(f"🔍 Instagram service created successfully")
                    
                    # Handle different post types
                    if post_type == 'carousel':
                        print(f"🔍 Processing carousel post...")
                        result = _handle_carousel_post(instagram_service, content, image_url, state)
                    elif post_type == 'video_reel':
                        print(f"🔍 Processing video reel post...")
                        result = _handle_video_reel_post(instagram_service, content, image_url, state)
                    elif post_type == 'story':
                        print(f"🔍 Processing story post...")
                        result = _handle_story_post(instagram_service, content, image_url, state)
                    else:
                        print(f"🔍 Processing single post...")
                        result = instagram_service.post_text_only(str(content), image_url=image_url)
                    
                    print(f"🔍 Instagram API response: {result}")
                    
                    if result['status'] == 'success':
                        print(f"🔍 ✅ Instagram post successful!")
                        social_data = {
                            'platform': 'instagram',
                            'post_type': post_type,
                            'content': content,
                            'access_token': access_token[:10] + '...',
                            'posted_at': result['posted_at'],
                            'post_id': result['instagram_post_id'],
                            'creation_id': result['creation_id'],
                            'real_post': True,
                            'api_response': result['api_response']
                        }
                        # Return a dictionary matching the declared 'writes' from the contract
                        return {'post_id': result.get('instagram_post_id')}
                    else:
                        print(f"🔍 ❌ Instagram post failed with status: {result.get('status')}")
                        print(f"🔍 Error details: {result.get('error', 'No error details')}")
                except Exception as e:
                    print(f"🔍 ❌ Instagram posting failed with exception: {e}")
                    import traceback
                    traceback.print_exc()
                    pass
                    
            # Fallback to simulation mode
            social_data = {
                'platform': 'instagram',
                'post_type': post_type,
                'content': content,
                'access_token': access_token[:10] + '...' if access_token else 'demo_token',
                'posted_at': datetime.now().isoformat(),
                'post_id': f"ig_post_{datetime.now().timestamp()}",
                'real_post': False,
                'simulation_mode': True,
                'image_url_used': image_url or 'none'
            }
            state['social_data'] = social_data
            # Return a dictionary matching the declared 'writes' from the contract
            return {'post_id': social_data.get('post_id', 'simulated_post_id')}
        else:
            social_data = {
                'platform': platform,
                'content': content,
                'posted_at': datetime.now().isoformat()
            }
            state['social_data'] = social_data
            state['status'] = 'posted'
            state['timestamp'] = datetime.now().isoformat()
            return state
    except Exception as e:
        print(f"Error in social media node: {e}")
        state['status'] = 'failed'
        state['error'] = str(e)
        state['timestamp'] = datetime.now().isoformat()
        return state


def _handle_carousel_post(instagram_service: InstagramService, content: str, image_url: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """Handle carousel post creation with multiple images"""
    try:
        print(f"📱 Processing carousel post with multiple images...")
        print(f"📱 State keys available: {list(state.keys())}")
        
        # First try to get uploaded carousel images (public URLs)
        uploaded_carousel_images = state.get('uploaded_carousel_images', [])
        carousel_image_urls = state.get('carousel_image_urls', [])
        
        print(f"📱 Uploaded carousel images count: {len(uploaded_carousel_images)}")
        print(f"📱 Carousel image URLs count: {len(carousel_image_urls)}")
        
        if uploaded_carousel_images and carousel_image_urls:
            print(f"✅ Found {len(carousel_image_urls)} uploaded carousel images")
            print(f"✅ Carousel image URLs: {carousel_image_urls}")
            if len(carousel_image_urls) >= 2:
                caption = f"{content}\n\n📊 Carousel post with {len(carousel_image_urls)} slides"
                print(f"📱 Posting carousel with {len(carousel_image_urls)} images to Instagram...")
                return instagram_service.post_carousel(caption, carousel_image_urls)
            else:
                print(f"❌ Not enough uploaded images for carousel (need 2+, got {len(carousel_image_urls)})")
        
        # Fallback to original carousel images (data URLs)
        carousel_images = state.get('carousel_images', [])
        print(f"📱 Original carousel images count: {len(carousel_images)}")
        
        if not carousel_images:
            print(f"❌ No carousel images found, falling back to single post")
            caption = f"{content}\n\n📊 Carousel post with multiple insights"
            return instagram_service.post_text_only(caption, image_url=image_url)
        
        # Extract image URLs from carousel images
        image_urls = []
        for i, slide in enumerate(carousel_images):
            if isinstance(slide, dict) and 'image_data_url' in slide:
                image_urls.append(slide['image_data_url'])
                print(f"📱 Slide {i+1}: Found image_data_url in slide dict")
            elif isinstance(slide, str):
                image_urls.append(slide)
                print(f"📱 Slide {i+1}: Found direct string URL")
            else:
                print(f"📱 Slide {i+1}: Invalid slide format: {type(slide)}")
        
        print(f"📱 Extracted {len(image_urls)} image URLs from carousel images")
        
        if len(image_urls) < 2:
            print(f"❌ Not enough images for carousel, falling back to single post")
            caption = f"{content}\n\n📊 Carousel post with multiple insights"
            return instagram_service.post_text_only(caption, image_url=image_url)
        
        # Create carousel caption
        caption = f"{content}\n\n📊 Carousel post with {len(image_urls)} slides"
        
        # Post carousel with multiple images
        print(f"📱 Posting carousel with {len(image_urls)} data URLs to Instagram...")
        return instagram_service.post_carousel(caption, image_urls)
        
    except Exception as e:
        print(f"❌ Carousel post failed: {e}")
        return {'status': 'failed', 'error': str(e)}


def _handle_video_reel_post(instagram_service: InstagramService, content: str, image_url: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """Handle video reel post creation"""
    try:
        # For now, create a single post with video reel content
        # In the future, this could handle actual video uploads
        caption = f"{content}\n\n🎥 Video reel content"
        return instagram_service.post_text_only(caption, image_url=image_url)
    except Exception as e:
        print(f"Video reel post failed: {e}")
        return {'status': 'failed', 'error': str(e)}


def _handle_story_post(instagram_service: InstagramService, content: str, image_url: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """Handle story post creation"""
    try:
        # For now, create a single post with story content
        # In the future, this could handle story-specific posting
        caption = f"{content}\n\n📱 Story content"
        return instagram_service.post_text_only(caption, image_url=image_url)
    except Exception as e:
        print(f"Story post failed: {e}")
        return {'status': 'failed', 'error': str(e)}


def execute_instagram(state: Dict[str, Any]) -> Dict[str, Any]:
    state.setdefault('platform', 'instagram')
    return execute(state)