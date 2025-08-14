from typing import Dict, Any

from .context import nodes_ctx


def data_node(state: Dict[str, Any]) -> Dict[str, Any]:
    return nodes_ctx.data_node(state)


def condition_node(state: Dict[str, Any]) -> Dict[str, Any]:
    return nodes_ctx.condition_node(state)


def delay_node(state: Dict[str, Any]) -> Dict[str, Any]:
    return nodes_ctx.delay_node(state)


def schedule_node(state: Dict[str, Any]) -> Dict[str, Any]:
    return nodes_ctx.schedule_node(state)


def transform_node(state: Dict[str, Any]) -> Dict[str, Any]:
    return nodes_ctx.transform_node(state)


def filter_node(state: Dict[str, Any]) -> Dict[str, Any]:
    return nodes_ctx.filter_node(state)


def aggregate_node(state: Dict[str, Any]) -> Dict[str, Any]:
    return nodes_ctx.aggregate_node(state)


def error_handler_node(state: Dict[str, Any]) -> Dict[str, Any]:
    return nodes_ctx.error_handler_node(state)