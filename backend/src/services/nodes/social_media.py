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
        print(f"🔍 SOCIAL MEDIA NODE DEBUG:" +content)
        if platform == 'instagram' or platform == 'instagram_post':
            # First try to get structured_data from AI Agent
            if 'structured_data' in state and state['structured_data']:
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
            if not image_url and image:
                if isinstance(image, dict) and 'image_url' in image:
                    image_url = image.get('image_url')
                elif isinstance(image, str):
                    image_url = image
            print(f"🔍 Content type: {type(content)}")
            
            if isinstance(content, dict):
                print(f"🔍 Content is a dict with keys: {list(content.keys())}")
                caption = content.get('caption', '')
                hashtags = content.get('hashtags', [])
                summary = content.get('summary', '')
                
                # Use summary if no caption
                if not caption and summary:
                    caption = summary[:200] + "..." if len(summary) > 200 else summary
                
                if hashtags:
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
            print(f"🔍 SOCIAL MEDIA NODE DEBUG:"+content)
            
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
                try:
                    print(f"🔍 Creating Instagram service...")
                    instagram_service = InstagramService(access_token)
                    print(f"🔍 Instagram service created successfully")
                    
                    print(f"🔍 Calling post_text_only...")
                    result = instagram_service.post_text_only(str(content), image_url=image_url)
                    print(f"🔍 Instagram API response: {result}")
                    
                    if result['status'] == 'success':
                        print(f"🔍 ✅ Instagram post successful!")
                        social_data = {
                            'platform': 'instagram',
                            'content': content,
                            'access_token': access_token[:10] + '...',
                            'posted_at': result['posted_at'],
                            'post_id': result['instagram_post_id'],
                            'creation_id': result['creation_id'],
                            'real_post': True,
                            'api_response': result['api_response']
                        }
                        state['social_data'] = social_data
                        state['instagram_post'] = social_data
                        state['status'] = 'posted'
                        state['timestamp'] = datetime.now().isoformat()
                        return state
                    else:
                        print(f"🔍 ❌ Instagram post failed with status: {result.get('status')}")
                        print(f"🔍 Error details: {result.get('error', 'No error details')}")
                except Exception as e:
                    print(f"🔍 ❌ Instagram posting failed with exception: {e}")
                    import traceback
                    traceback.print_exc()
                    pass
            social_data = {
                'platform': 'instagram',
                'content': content,
                'access_token': access_token[:10] + '...' if access_token else 'demo_token',
                'posted_at': datetime.now().isoformat(),
                'post_id': f"ig_post_{datetime.now().timestamp()}",
                'real_post': False,
                'simulation_mode': True,
                'image_url_used': image_url or 'none'
            }
            state['social_data'] = social_data
            state['instagram_post'] = social_data
            state['status'] = 'posted'
            state['timestamp'] = datetime.now().isoformat()
            return state
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


def execute_instagram(state: Dict[str, Any]) -> Dict[str, Any]:
    state.setdefault('platform', 'instagram')
    return execute(state)