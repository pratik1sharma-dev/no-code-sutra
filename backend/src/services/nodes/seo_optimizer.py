from typing import Dict, Any
from datetime import datetime
from ..contracts import SeoOptimizerInputV1, SeoOptimizerOutputV1


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        inp = SeoOptimizerInputV1(
            content=state.get('content', ''),
            target_keywords=state.get('target_keywords', [])
        )
        optimized = inp.content + ("\n\n# " + " #".join([k.replace('#','') for k in inp.target_keywords]) if inp.target_keywords else "")
        out = SeoOptimizerOutputV1(
            original_content=inp.content,
            optimized_content=optimized,
            target_keywords=inp.target_keywords,
            optimized_at=datetime.now().isoformat()
        )
        state['seo_data'] = out.model_dump()
        state['status'] = 'completed'
        state['timestamp'] = datetime.now().isoformat()
        return state
    except Exception as e:
        state['status'] = 'failed'
        state['error'] = str(e)
        return state