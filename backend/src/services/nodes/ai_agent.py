from typing import Dict, Any
from datetime import datetime

from ..llm.factory import get_llm_client


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

        if prompt:
            # Enhanced system prompt with template awareness for workflow-generated prompts
            system_prompt = """You are an AI content generation agent with Instagram design expertise. 

AVAILABLE INSTAGRAM TEMPLATES:
- "minimal": Clean, professional design with elegant typography (best for: business, professional, corporate)
- "bold": High-impact design with strong contrast (best for: motivational, promotional, urgent messages)
- "gradient": Modern design with colorful gradients (best for: tech, lifestyle, creative content)
- "split_screen": Organized layout with content on one side (best for: educational, tutorials, features)
- "quote": Elegant quote-focused design (best for: inspirational quotes, testimonials, wisdom)

You MUST follow the instructions exactly and return ONLY valid JSON without any additional text, explanations, or formatting.

You MAY optionally include a "recommended_template" field if you think a specific template would work particularly well for this content."""
            user_prompt = prompt  # Use the workflow-generated contextual prompt
        else:
            if task == 'research':
                system_prompt = f"You are an AI research agent. Research the topic: {topic}"
                user_prompt = f"Please provide comprehensive research on: {topic}"
            elif task == 'generate':
                system_prompt = f"""You are an AI content generation agent with Instagram design expertise.

AVAILABLE INSTAGRAM TEMPLATES:
- "minimal": Clean, professional design (best for: business, professional, corporate)
- "bold": High-impact design with strong contrast (best for: motivational, promotional)
- "gradient": Modern colorful design (best for: tech, lifestyle, creative)
- "split_screen": Organized educational layout (best for: tutorials, features)
- "quote": Elegant quote-focused design (best for: inspirational quotes)

Generate structured Instagram content with template recommendation."""
                user_prompt = f"""Generate engaging Instagram content about: {topic}

Return JSON with this structure:
{{
  "headline": "Main headline (under 40 characters)",
  "subhead": "Supporting description",
  "bullets": ["Point 1", "Point 2", "Point 3"],
  "caption": "Instagram caption with hashtags",
  "hashtags": ["hashtag1", "hashtag2", "hashtag3"]
}}

Optionally, if you think a specific visual template would work particularly well, you can include:
{{
  "recommended_template": "template_name",
  "template_reason": "Why this template works best"
}}"""
            elif task == 'analyze':
                system_prompt = f"You are an AI analysis agent. Analyze the topic: {topic}"
                user_prompt = f"Please provide detailed analysis of: {topic}"
            else:
                system_prompt = f"You are an intelligent AI agent. Process the given input and provide a helpful response."
                user_prompt = f"Context: {context}\n\nTask: {prompt}\n\nTopic: {topic}"

        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        response_content = llm.generate(full_prompt)

        # Try to parse JSON
        parsed_json = None
        try:
            json_start = response_content.find('{')
            json_end = response_content.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                import json as _json
                json_str = response_content[json_start:json_end]
                parsed_json = _json.loads(json_str)
        except Exception:
            parsed_json = None

        if parsed_json:
            state['result'] = parsed_json
            state['output'] = parsed_json
            state['content'] = response_content
            state['structured_data'] = parsed_json
        else:
            state['result'] = response_content
            state['output'] = response_content
            state['content'] = response_content

        state['task'] = task
        state['topic'] = topic
        state['status'] = 'completed'
        state['timestamp'] = datetime.now().isoformat()
        return state
    except Exception as e:
        state['status'] = 'failed'
        state['error'] = str(e)
        state['timestamp'] = datetime.now().isoformat()
        return state