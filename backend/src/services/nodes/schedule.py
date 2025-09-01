from typing import Dict, Any
from datetime import datetime
from ..contracts import ScheduleInputV1, ScheduleOutputV1


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        inp = ScheduleInputV1(
            schedule_type=state.get('schedule_type', 'daily'),
            schedule_time=state.get('schedule_time', '09:00')
        )
        out = ScheduleOutputV1(type=inp.schedule_type, time=inp.schedule_time, created_at=datetime.now().isoformat())
        state['schedule_data'] = out.model_dump()
        state['status'] = 'scheduled'
        state['timestamp'] = datetime.now().isoformat()
        return state
    except Exception as e:
        state['status'] = 'failed'
        state['error'] = str(e)
        return state