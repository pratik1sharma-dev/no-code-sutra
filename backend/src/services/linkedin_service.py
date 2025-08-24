import requests
from typing import Optional, Dict, Any
from datetime import datetime


class LinkedInService:
	"""Minimal LinkedIn posting service (member posts with optional image URL)"""

	def __init__(self, access_token: str):
		self.access_token = access_token
		self.api_base = 'https://api.linkedin.com/v2'

	def _headers(self) -> Dict[str, str]:
		return {
			'Authorization': f'Bearer {self.access_token}',
			'X-Restli-Protocol-Version': '2.0.0',
			'Content-Type': 'application/json'
		}

	def post_text(self, content: str, author_urn: Optional[str] = None, image_url: Optional[str] = None) -> Dict[str, Any]:
		"""Create a UGC Post on LinkedIn member feed with optional external image"""
		if not author_urn:
			# Best effort: fetch profile id to build author urn
			me = requests.get(f'{self.api_base}/me', headers=self._headers())
			me.raise_for_status()
			profile = me.json()
			pid = profile.get('id')
			author_urn = f'urn:li:person:{pid}' if pid else None

		ugc_body: Dict[str, Any] = {
			"author": author_urn,
			"lifecycleState": "PUBLISHED",
			"specificContent": {
				"com.linkedin.ugc.ShareContent": {
					"shareCommentary": {"text": content[:2900]},
					"shareMediaCategory": "NONE"
				}
			},
			"visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
		}
		if image_url:
			ugc_body["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "ARTICLE"
			ugc_body["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
				{
					"status": "READY",
					"originalUrl": image_url,
					"title": {"text": ""}
				}
			]

		resp = requests.post(f'{self.api_base}/ugcPosts', headers=self._headers(), json=ugc_body)
		real_post = resp.status_code in (201, 202)
		data = {}
		try:
			resp.raise_for_status()
			data = resp.json()
		except Exception:
			data = {"error": resp.text}
		return {
			"id": data.get('id'),
			"author_urn": author_urn,
			"api_response": data,
			"posted_at": datetime.now().isoformat(),
			"real_post": real_post
		}

