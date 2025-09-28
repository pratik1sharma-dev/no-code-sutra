from typing import Dict, Any
from datetime import datetime
from ..contracts import SlackInputV1, SlackOutputV1


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        channel = state.get('channel', '')
        message = state.get('message') or state.get('text') or ''
        inp = SlackInputV1(channel=channel, message=message)
        sent_at = datetime.now().isoformat()
        out = SlackOutputV1(message_ts=None, status='sent', sent_at=sent_at)

        state['slack_input'] = inp.model_dump()
        state['slack_data'] = {
            'channel': inp.channel,
            'message': inp.message,
            'sent_at': sent_at
        }
        state['status'] = out.status
        state['timestamp'] = sent_at
        return state
    except Exception as e:
        state['status'] = 'failed'
        state['error'] = str(e)
        return state