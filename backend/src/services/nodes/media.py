from typing import Dict, Any

from .context import nodes_ctx


def text_overlay_node(state: Dict[str, Any]) -> Dict[str, Any]:
    return nodes_ctx.text_overlay_node(state)


def image_generator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    return nodes_ctx.image_generator_node(state)


def image_upload_node(state: Dict[str, Any]) -> Dict[str, Any]:
    return nodes_ctx.image_upload_node(state)