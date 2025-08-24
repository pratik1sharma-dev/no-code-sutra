import json
from typing import Dict, Any
from datetime import datetime

from ..linkedin_credentials import linkedin_credentials_service
from ..linkedin_service import LinkedInService


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
	try:
		user_id = state.get('user_id', 'default_user')
		structured = state.get('ai_output') or state.get('structured_data') or state.get('content')
		image_url = state.get('image_url') or state.get('image')
		author_urn = state.get('author_urn')

		if not structured:
			state['status'] = 'failed'
			state['error'] = 'No content available for LinkedIn post'
			state['timestamp'] = datetime.now().isoformat()
			return state

		# Normalize content
		if isinstance(structured, dict):
			content = structured.get('content') or structured.get('caption') or structured.get('summary') or ''
			hashtags = structured.get('hashtags') or []
			if hashtags:
				hashtag_text = ' '.join([f"#{str(tag).replace('#', '')}" for tag in hashtags])
				content = f"{content}\n\n{hashtag_text}".strip()
		else:
			content = str(structured)

		if not content:
			state['status'] = 'failed'
			state['error'] = 'Empty LinkedIn post content'
			state['timestamp'] = datetime.now().isoformat()
			return state

		access_token = linkedin_credentials_service.get_access_token(user_id)
		if not access_token:
			state['status'] = 'failed'
			state['error'] = 'No valid LinkedIn credentials found'
			state['timestamp'] = datetime.now().isoformat()
			return state

		creds = linkedin_credentials_service.get_credentials(user_id) or {}
		author = author_urn or creds.get('author_urn')
		service = LinkedInService(access_token)
		result = service.post_text(content=content, author_urn=author, image_url=image_url)

		state['linkedin_post'] = {
			'platform': 'linkedin',
			'content': content[:2000],
			'author_urn': result.get('author_urn') or author,
			'post_id': result.get('post_id') or result.get('id'),
			'posted_at': result.get('posted_at') or datetime.now().isoformat(),
			'real_post': result.get('real_post', False),
		}
		state['status'] = 'posted'
		state['timestamp'] = datetime.now().isoformat()
		return state
	except Exception as e:
		state['status'] = 'failed'
		state['error'] = str(e)
		state['timestamp'] = datetime.now().isoformat()
		return state

