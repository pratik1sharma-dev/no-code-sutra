from typing import Dict, Any
from datetime import datetime

from ..llm.factory import get_llm_client
from ..contracts import ContentV1, normalize_to_content_v1


def extract_response_format(prompt: str) -> str:
    """Extract the exact response format from the workflow prompt"""
    import re
    
    # Look for "Return JSON:" patterns
    json_patterns = [
        r'Return JSON:\s*(\{.*?\})',
        r'Return:\s*(\{.*?\})',
        r'JSON:\s*(\{.*?\})',
        r'Format:\s*(\{.*?\})'
    ]
    
    for pattern in json_patterns:
        match = re.search(pattern, prompt, re.DOTALL)
        if match:
            return match.group(1)
    
    return None


def detect_content_type(prompt: str) -> str:
    """Detect the content type based on the user prompt."""
    prompt_lower = prompt.lower()
    
    # Check for character story indicators
    if any(keyword in prompt_lower for keyword in [
        "character story", "character", "storytelling", "story with character",
        "create a character", "character-based", "story about a character"
    ]):
        return "character_story"
    
    # Check for Instagram post indicators
    elif any(keyword in prompt_lower for keyword in [
        "instagram", "instagram post", "social media post", "post on instagram",
        "instagram content", "social media content"
    ]):
        return "instagram_post"
    
    # Default to general content
    else:
        return "general"


def get_fallback_system_prompt(content_type: str) -> str:
    """Get fallback system prompt based on content type"""
    if content_type == "character_story":
        return """You are an AI content generation agent specializing in character-based storytelling.

CRITICAL: You MUST return this exact JSON structure:
{
  "headline": "Character name or story title",
  "subhead": "Brief character description", 
  "slides": [
    {
      "headline": "Story moment title",
      "subhead": "Character context",
      "story_line": "Detailed story content for this moment",
      "expression": "character emotion/expression"
    }
  ],
  "caption": "Instagram caption with hashtags",
  "hashtags": ["relevant", "hashtags"]
}

Each slide represents a story moment. The character should be consistent across all slides.

You MUST follow the instructions exactly and return ONLY valid JSON without any additional text, explanations, or formatting."""

    elif content_type == "instagram_post":
        return """You are an AI content generation agent for Instagram posts.

CRITICAL: You MUST return this exact JSON structure:
{
  "headline": "Main message (under 40 characters)",
  "subhead": "Supporting description (optional)",
  "bullets": ["Point 1", "Point 2", "Point 3"] (optional),
  "caption": "Instagram caption with hashtags",
  "hashtags": ["hashtag1", "hashtag2", "hashtag3"],
  "recommended_template": "quote|minimal|bold|gradient|split_screen"
}

You MUST follow the instructions exactly and return ONLY valid JSON without any additional text, explanations, or formatting."""

    else:
        return """You are an AI content generation agent.

CRITICAL: You MUST return this exact JSON structure:
{
  "headline": "Main message",
  "subhead": "Supporting description",
  "content": "Main content text",
  "caption": "Instagram caption with hashtags", 
  "hashtags": ["relevant", "hashtags"]
}

You MUST follow the instructions exactly and return ONLY valid JSON without any additional text, explanations, or formatting."""


def build_dynamic_system_prompt(prompt: str) -> str:
    """Build dynamic system prompt based on workflow format or content type"""
    # Always try to use the workflow's exact format first
    response_format = extract_response_format(prompt)
    
    if response_format:
        # No conflicts - use workflow format exactly
        return f"""You are an AI content generation agent.

CRITICAL: You MUST return this exact JSON structure:
{response_format}

You MUST follow the instructions exactly and return ONLY valid JSON without any additional text, explanations, or formatting."""
    
    # Only fallback if no format found in prompt
    content_type = detect_content_type(prompt)
    return get_fallback_system_prompt(content_type)


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        llm = get_llm_client()
        if llm is None:
            state['status'] = 'failed'
            state['error'] = 'LLM not available'
            state['timestamp'] = datetime.now().isoformat()
            return state

        prompt = state.get('prompt', '')
        task = state.get('task', 'generate')
        topic = state.get('topic', 'content generation')
        context = state.get('context', '')

        # Detect content type from prompt (if available)
        content_type = detect_content_type(prompt) if prompt else "general"
        
        if prompt:
            # Use dynamic system prompt that extracts format from workflow or falls back to content type
            system_prompt = build_dynamic_system_prompt(prompt)
            user_prompt = prompt  # Use the workflow-generated contextual prompt
        else:
            # Fallback for when no prompt is provided
            system_prompt = f"You are an intelligent AI agent. Process the given input and provide a helpful response."
            user_prompt = f"Context: {context}\n\nTask: {prompt}\n\nTopic: {topic}"

        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        response_content = llm.generate(full_prompt)

        # Parse JSON and normalize to canonical schema with a light repair attempt
        parsed_json = None
        for attempt in range(2):  # try once, then a repair re-prompt if needed
            try:
                json_start = response_content.find('{')
                json_end = response_content.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    import json as _json
                    json_str = response_content[json_start:json_end]
                    parsed_json = _json.loads(json_str)
            except Exception:
                parsed_json = None

            try:
                normalized = normalize_to_content_v1(parsed_json if parsed_json is not None else response_content)
                # Validate against ContentV1
                content_obj = ContentV1(**normalized)
                # Success
                state['raw_response'] = response_content
                state['result'] = content_obj.model_dump()
                state['output'] = state['result']
                state['content'] = state['result']
                state['structured_data'] = state['result']
                break
            except Exception:
                # Repair: ask model to fix to exact schema
                if attempt == 0:
                    # Try to extract format from original prompt for repair
                    response_format = extract_response_format(prompt) if prompt else None
                    
                    if response_format:
                        # Use the same format for repair
                        repair_schema = response_format
                    else:
                        # Fallback to content type based schema
                        if content_type == "character_story":
                            repair_schema = '{"headline": string, "subhead": string, "slides": [{"headline": string, "subhead": string, "story_line": string, "expression": string}], "caption": string, "hashtags": string[]}'
                        elif content_type == "instagram_post":
                            repair_schema = '{"headline": string, "subhead": string, "bullets": string[], "caption": string, "hashtags": string[]}'
                        else:
                            repair_schema = '{"headline": string, "subhead": string, "content": string, "caption": string, "hashtags": string[]}'
                    
                    repair_prompt = (
                        "Return ONLY valid JSON matching this schema: "
                        f"{repair_schema} "
                        f"Fix the previous output. Topic: {topic}"
                    )
                    response_content = llm.generate(repair_prompt)
                    continue
                else:
                    # Last resort: wrap as minimal content
                    fallback = ContentV1(headline=str(topic)[:40] if topic else "", caption=str(response_content)).model_dump()
                    state['raw_response'] = response_content
                    state['result'] = fallback
                    state['output'] = fallback
                    state['content'] = fallback
                    state['structured_data'] = fallback
                    break

        state['task'] = task
        state['topic'] = topic
        state['status'] = 'completed'
        state['timestamp'] = datetime.now().isoformat()

        # Return the structured data in the format expected by the contract
        return {
            'structured_data': state['structured_data']
        }
    except Exception as e:
        state['status'] = 'failed'
        state['error'] = str(e)
        state['timestamp'] = datetime.now().isoformat()
        # Even on failure, return the expected structure
        return {
            'structured_data': {'error': str(e), 'status': 'failed'}
        }