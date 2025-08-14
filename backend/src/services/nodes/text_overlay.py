from typing import Dict, Any

from .context import nodes_ctx


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    return nodes_ctx.text_overlay_node(state)