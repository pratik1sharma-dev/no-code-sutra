from typing import Dict, Any
from datetime import datetime


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        topic = state.get('topic', 'blog topic')
        style = state.get('style', 'professional')
        length = state.get('length', 'medium')
        content = f"[{style} | {length}] Draft blog about: {topic}"
        blog_data = {
            'topic': topic,
            'content': content,
            'style': style,
            'length': length,
            'generated_at': datetime.now().isoformat()
        }
        state['blog_data'] = blog_data
        state['status'] = 'completed'
        state['timestamp'] = datetime.now().isoformat()
        return state
    except Exception as e:
        state['status'] = 'failed'
        state['error'] = str(e)
        return state