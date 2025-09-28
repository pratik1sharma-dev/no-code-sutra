import os
import requests
from typing import Optional

from .base import LLMClient


class BedrockClient(LLMClient):
    """Amazon Bedrock bearer-token based client adapter."""

    def __init__(self, model_id: Optional[str] = None, region: Optional[str] = None, system_prompt: Optional[str] = None) -> None:
        # Use configured model (prefer 70B model)
        self.model_id = model_id or os.getenv("BEDROCK_MODEL_ID", "meta.llama3-1-70b-instruct-v1:0")
        self.region = region or os.getenv("AWS_DEFAULT_REGION", "us-west-2")
        self.token = os.getenv("AWS_BEARER_TOKEN_BEDROCK", "")
        self.system_prompt = system_prompt
        
        # Log model configuration
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Bedrock client initialized with model: {self.model_id} in region: {self.region}")
        
        if "70b" in self.model_id.lower():
            logger.info("Using Llama 3.1 70B model - ensure model access is enabled in AWS Bedrock Console")
        elif "8b" in self.model_id.lower():
            logger.info("Using Llama 3.1 8B model")
        else:
            logger.warning(f"Unknown model type: {self.model_id}")

    def generate(self, prompt: str, *, timeout: float | None = 120.0, system_prompt: Optional[str] = None) -> str:
        if not self.token:
            raise RuntimeError("AWS_BEARER_TOKEN_BEDROCK not configured")
        url = f"https://bedrock-runtime.{self.region}.amazonaws.com/model/{self.model_id}/converse"
        
        # Use provided system prompt or instance default
        sys_prompt = system_prompt or self.system_prompt
        
        # Build messages array with proper Bedrock Converse API format
        messages = []
        messages.append({"role": "user", "content": [{"text": prompt}]})
        
        # For Bedrock Converse API, system prompt goes in a separate field
        payload = {"messages": messages}
        if sys_prompt:
            payload["system"] = [{"text": sys_prompt}]
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        
        # Add debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Bedrock request URL: {url}")
        logger.info(f"Bedrock model: {self.model_id}")
        logger.info(f"Bedrock region: {self.region}")
        logger.info(f"System prompt length: {len(sys_prompt) if sys_prompt else 0}")
        logger.info(f"User prompt length: {len(prompt)}")
        logger.info(f"Total messages: {len(messages)}")
        
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=timeout or 120.0)
            
            # Log response details for debugging
            logger.info(f"Response status: {resp.status_code}")
            if resp.status_code != 200:
                logger.error(f"Response headers: {dict(resp.headers)}")
                logger.error(f"Response body: {resp.text}")
                
                # Handle specific Bedrock errors
                if resp.status_code == 400:
                    error_body = resp.text
                    if "model" in error_body.lower() and "not found" in error_body.lower():
                        logger.error(f"Model {self.model_id} not available in region {self.region}")
                        raise RuntimeError(f"Bedrock model {self.model_id} not available in region {self.region}. Check model access permissions in AWS Console.")
                    elif "access" in error_body.lower() or "permission" in error_body.lower():
                        logger.error("Access denied to Bedrock model")
                        raise RuntimeError(f"Access denied to Bedrock model {self.model_id}. Enable model access in AWS Bedrock Console.")
                    elif "token" in error_body.lower() or "auth" in error_body.lower():
                        logger.error("Authentication failed")
                        raise RuntimeError("Bedrock authentication failed. Check AWS_BEARER_TOKEN_BEDROCK environment variable.")
                    else:
                        logger.error(f"Bedrock API error: {error_body}")
                        raise RuntimeError(f"Bedrock API error: {error_body}")
            
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise RuntimeError(f"Failed to connect to Bedrock API: {e}")
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