from typing import Dict, Any

from .base import NodeExecutor
from .context import nodes_ctx


def ai_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    return nodes_ctx.ai_agent_node(state)