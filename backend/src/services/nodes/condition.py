from typing import Dict, Any
from datetime import datetime


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        condition = state.get('condition', '')
        input_value = state.get('input_value', '')
        result = _evaluate_condition(condition, input_value)
        state['condition_result'] = result
        state['next_step'] = 'branch_a' if result else 'branch_b'
        state['status'] = 'completed'
        state['timestamp'] = datetime.now().isoformat()
        return state
    except Exception as e:
        state['status'] = 'failed'
        state['error'] = str(e)
        return state


def _evaluate_condition(condition: str, value: Any) -> bool:  # type: ignore[name-defined]
    try:
        cl = condition.lower()
        if 'contains' in cl:
            return str(value).lower() in cl
        if '>' in condition or 'greater' in cl:
            return float(value) > 0
        if '<' in condition or 'less' in cl:
            return float(value) < 0
        return bool(value)
    except Exception:
        return False