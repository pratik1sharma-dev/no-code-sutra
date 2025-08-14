from typing import Dict, Any

from .context import nodes_ctx


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    return nodes_ctx.social_media_node(state)


def execute_instagram(state: Dict[str, Any]) -> Dict[str, Any]:
    state.setdefault('platform', 'instagram')
    return nodes_ctx.social_media_node(state)