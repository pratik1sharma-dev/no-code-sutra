from typing import Dict, Any
from datetime import datetime


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        schedule_type = state.get('schedule_type', 'daily')
        schedule_time = state.get('schedule_time', '09:00')
        schedule_data = {
            'type': schedule_type,
            'time': schedule_time,
            'created_at': datetime.now().isoformat()
        }
        state['schedule_data'] = schedule_data
        state['status'] = 'scheduled'
        state['timestamp'] = datetime.now().isoformat()
        return state
    except Exception as e:
        state['status'] = 'failed'
        state['error'] = str(e)
        return state