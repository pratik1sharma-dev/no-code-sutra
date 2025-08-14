from typing import Dict, Any

from .context import nodes_ctx


def email_node(state: Dict[str, Any]) -> Dict[str, Any]:
    return nodes_ctx.email_node(state)


def slack_node(state: Dict[str, Any]) -> Dict[str, Any]:
    return nodes_ctx.slack_node(state)


def notification_node(state: Dict[str, Any]) -> Dict[str, Any]:
    return nodes_ctx.notification_node(state)