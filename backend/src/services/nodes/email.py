from typing import Dict, Any
from datetime import datetime


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        to_email = state.get('to_email', '')
        subject = state.get('subject', '')
        body = state.get('body', '')
        email_data = {
            'to': to_email,
            'subject': subject,
            'body': body,
            'sent_at': datetime.now().isoformat()
        }
        state['email_data'] = email_data
        state['status'] = 'sent'
        state['timestamp'] = datetime.now().isoformat()
        return state
    except Exception as e:
        state['status'] = 'failed'
        state['error'] = str(e)
        return state