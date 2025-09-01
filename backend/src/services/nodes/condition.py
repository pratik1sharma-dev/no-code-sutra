from typing import Dict, Any
from datetime import datetime
from ..contracts import ConditionInputV1, ConditionOutputV1


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        inp = ConditionInputV1(condition=state.get('condition', ''), input_value=state.get('input_value'))
        result = _evaluate_condition(inp.condition, inp.input_value)
        out = ConditionOutputV1(condition_result=result, next_step='branch_a' if result else 'branch_b')
        state['condition_result'] = out.condition_result
        state['next_step'] = out.next_step
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