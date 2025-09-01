from typing import Dict, Any
from datetime import datetime
from ..contracts import BlogWriterInputV1, BlogWriterOutputV1


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        inp = BlogWriterInputV1(
            topic=state.get('topic', 'blog topic'),
            style=state.get('style', 'professional'),
            length=state.get('length', 'medium')
        )
        content = f"[{inp.style} | {inp.length}] Draft blog about: {inp.topic}"
        out = BlogWriterOutputV1(
            topic=inp.topic,
            content=content,
            style=inp.style,
            length=inp.length,
            generated_at=datetime.now().isoformat()
        )
        state['blog_data'] = out.model_dump()
        state['status'] = 'completed'
        state['timestamp'] = datetime.now().isoformat()
        return state
    except Exception as e:
        state['status'] = 'failed'
        state['error'] = str(e)
        return state