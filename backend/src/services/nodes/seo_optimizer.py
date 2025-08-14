from typing import Dict, Any
from datetime import datetime


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        content = state.get('content', '')
        target_keywords = state.get('target_keywords', [])
        optimized = content + ("\n\n# " + " #".join([k.replace('#','') for k in target_keywords]) if target_keywords else "")
        seo_data = {
            'original_content': content,
            'optimized_content': optimized,
            'target_keywords': target_keywords,
            'optimized_at': datetime.now().isoformat()
        }
        state['seo_data'] = seo_data
        state['status'] = 'completed'
        state['timestamp'] = datetime.now().isoformat()
        return state
    except Exception as e:
        state['status'] = 'failed'
        state['error'] = str(e)
        return state