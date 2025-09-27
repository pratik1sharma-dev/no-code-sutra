import os
import requests
from typing import Optional

from .base import LLMClient


class BedrockClient(LLMClient):
    """Amazon Bedrock bearer-token based client adapter."""

    def __init__(self, model_id: Optional[str] = None, region: Optional[str] = None, system_prompt: Optional[str] = None) -> None:
        self.model_id = model_id or os.getenv("BEDROCK_MODEL_ID", "meta.llama3-1-8b-instruct-v1:0")
        self.region = region or os.getenv("AWS_DEFAULT_REGION", "ap-southeast-1")
        self.token = os.getenv("AWS_BEARER_TOKEN_BEDROCK", "")
        self.system_prompt = system_prompt

    def generate(self, prompt: str, *, timeout: float | None = 120.0, system_prompt: Optional[str] = None) -> str:
        if not self.token:
            raise RuntimeError("AWS_BEARER_TOKEN_BEDROCK not configured")
        url = f"https://bedrock-runtime.{self.region}.amazonaws.com/model/{self.model_id}/converse"
        
        # Use provided system prompt or instance default
        sys_prompt = system_prompt or self.system_prompt
        
        # Build messages array with proper roles
        messages = []
        if sys_prompt:
            messages.append({"role": "system", "content": [{"text": sys_prompt}]})
        messages.append({"role": "user", "content": [{"text": prompt}]})
        
        payload = {"messages": messages}
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout or 120.0)
        resp.raise_for_status()
        data = resp.json()
        # Attempt common shapes
        if 'content' in data:
            return data['content'][0]['text']
        if 'message' in data:
            return data['message']['content'][0]['text']
        if 'output' in data and 'message' in data['output']:
            return data['output']['message']['content'][0]['text']
        if 'generation' in data:
            return data['generation']
        raise RuntimeError("Unexpected response structure from Bedrock API")