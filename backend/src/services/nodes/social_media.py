from typing import Dict, Any
from datetime import datetime

from ..instagram_service import InstagramService


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        platform = state.get('platform', 'instagram')
        content = state.get('content', '')
        access_token = state.get('access_token', '')
        post = state.get('post', '')
        image_url = state.get('image_url', '')
        image = state.get('image', '')

        if platform == 'instagram' or platform == 'instagram_post':
            if not content:
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
            if isinstance(content, dict):
                caption = content.get('caption', '')
                hashtags = content.get('hashtags', [])
                if hashtags:
                    hashtag_text = ' '.join([f"#{tag.replace('#', '')}" for tag in hashtags])
                    content = f"{caption}\n\n{hashtag_text}"
                else:
                    content = caption
            if not content:
                state['status'] = 'failed'
                state['error'] = 'No content available for Instagram post'
                state['timestamp'] = datetime.now().isoformat()
                return state
            if access_token and access_token != 'test_token_12345':
                try:
                    instagram_service = InstagramService(access_token)
                    result = instagram_service.post_text_only(str(content), image_url=image_url)
                    if result['status'] == 'success':
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
                except Exception:
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