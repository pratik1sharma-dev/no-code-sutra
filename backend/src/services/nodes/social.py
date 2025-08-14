from typing import Dict, Any

from .context import nodes_ctx


def social_media_node(state: Dict[str, Any]) -> Dict[str, Any]:
    return nodes_ctx.social_media_node(state)


def instagram_post_node(state: Dict[str, Any]) -> Dict[str, Any]:
    # Alias to social media node with instagram in state
    state.setdefault('platform', 'instagram')
    return nodes_ctx.social_media_node(state)