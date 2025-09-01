from typing import Dict, Any
from datetime import datetime
from ..contracts import DelayInputV1, DelayOutputV1


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        inp = DelayInputV1(delay_seconds=int(state.get('delay_seconds', 1)))
        scheduled_for = datetime.now().isoformat()
        out = DelayOutputV1(scheduled_for=scheduled_for)
        state['delay_seconds'] = inp.delay_seconds
        state['scheduled_for'] = out.scheduled_for
        state['status'] = 'scheduled'
        state['timestamp'] = datetime.now().isoformat()
        return state
    except Exception as e:
        state['status'] = 'failed'
        state['error'] = str(e)
        return state