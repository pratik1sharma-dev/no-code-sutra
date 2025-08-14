from typing import Dict, Any
from datetime import datetime


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        prompt = state.get('prompt', '')
        style = state.get('style', 'realistic')
        image_url = f"https://picsum.photos/seed/{int(datetime.now().timestamp())}/1080/1080"
        image_data = {
            'prompt': prompt,
            'style': style,
            'image_url': image_url,
            'generated_at': datetime.now().isoformat()
        }
        state['image_data'] = image_data
        state['image_url'] = image_url
        state['image'] = image_data
        state['status'] = 'completed'
        state['timestamp'] = datetime.now().isoformat()
        return state
    except Exception as e:
        state['status'] = 'failed'
        state['error'] = str(e)
        return state