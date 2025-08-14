from typing import Dict, Any
from datetime import datetime


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        channel = state.get('channel', '')
        message = state.get('message', '')
        slack_data = {
            'channel': channel,
            'message': message,
            'sent_at': datetime.now().isoformat()
        }
        state['slack_data'] = slack_data
        state['status'] = 'sent'
        state['timestamp'] = datetime.now().isoformat()
        return state
    except Exception as e:
        state['status'] = 'failed'
        state['error'] = str(e)
        return state