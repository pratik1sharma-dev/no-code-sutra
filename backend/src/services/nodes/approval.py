from typing import Dict, Any
from datetime import datetime


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    """Approval node that pauses the workflow until a decision is provided.
    Inputs (reads): overlay preview or content, approver info, optional reason.
    Writes: approval_status, approval_timestamp, approved_content/image
    """
    try:
        decision = state.get('approval_decision')  # 'approve' | 'reject' | None
        reason = state.get('approval_reason', '')
        preview = state.get('image_url') or state.get('content')

        if decision is None:
            # Emit pending state expecting human decision
            return {
                **state,
                'status': 'pending_approval',
                'approval_required': True,
                'approval_preview': preview,
                'timestamp': datetime.now().isoformat()
            }

        # Decision provided: finalize
        approved = decision == 'approve'
        state['approval_required'] = False
        state['approval_status'] = 'approved' if approved else 'rejected'
        state['approval_reason'] = reason
        state['approval_timestamp'] = datetime.now().isoformat()
        state['status'] = 'completed' if approved else 'halted'
        return state
    except Exception as e:
        state['status'] = 'failed'
        state['error'] = str(e)
        state['timestamp'] = datetime.now().isoformat()
        return state