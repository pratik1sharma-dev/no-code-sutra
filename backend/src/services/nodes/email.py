from typing import Dict, Any
from datetime import datetime
from ..contracts import EmailInputV1, EmailOutputV1


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # Normalize input
        to_email = state.get('to_email') or state.get('to') or ''
        subject = state.get('subject', '')
        body = state.get('body') or state.get('message') or ''
        inp = EmailInputV1(to=to_email, subject=subject, body=body)

        # Here we would call a provider; simulate success
        sent_at = datetime.now().isoformat()
        out = EmailOutputV1(message_id=None, status='sent', sent_at=sent_at)

        state['email_input'] = inp.model_dump()
        state['email_data'] = {
            'to': inp.to,
            'subject': inp.subject,
            'body': inp.body,
            'sent_at': sent_at
        }
        state['status'] = out.status
        state['timestamp'] = sent_at
        return state
    except Exception as e:
        state['status'] = 'failed'
        state['error'] = str(e)
        return state