import os
from typing import Optional

from .base import LLMClient
from .bedrock_client import BedrockClient
try:
    from .openai_client import OpenAIClient  # Optional
except Exception:  # pragma: no cover
    OpenAIClient = None  # type: ignore


def get_llm_client() -> Optional[LLMClient]:
    provider = os.getenv("LLM_PROVIDER", "bedrock").lower()
    if provider == "bedrock":
        if os.getenv("AWS_BEARER_TOKEN_BEDROCK"):
            return BedrockClient()
    if provider == "openai" or not os.getenv("AWS_BEARER_TOKEN_BEDROCK"):
        if OpenAIClient and os.getenv("OPENAI_API_KEY"):
            return OpenAIClient()
    return None