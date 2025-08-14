from typing import Callable, Dict

from .nodes import ai as ai_nodes
from .nodes import communication as comm_nodes
from .nodes import data as data_nodes
from .nodes import media as media_nodes
from .nodes import social as social_nodes
from .langgraph_nodes.workflow_nodes import LangGraphWorkflowNodes


class NodeDispatcher:
    """Maps node types to executor callables.

    This enables extensibility (OCP) by centralizing the mapping between a
    string node type and the function that can execute that node. The mapping
    can be extended without changing core executor logic.
    """

    def __init__(self, nodes: LangGraphWorkflowNodes) -> None:
        # nodes retained for backward compat; modular executors delegate via shared context
        self._nodes = nodes
        self._dispatch: Dict[str, Callable] = {
            "aiAgent": ai_nodes.ai_agent_node,
            "email": comm_nodes.email_node,
            "slack": comm_nodes.slack_node,
            "notification": comm_nodes.notification_node,
            "data": data_nodes.data_node,
            "condition": data_nodes.condition_node,
            "delay": data_nodes.delay_node,
            "schedule": data_nodes.schedule_node,
            "transform": data_nodes.transform_node,
            "filter": data_nodes.filter_node,
            "aggregate": data_nodes.aggregate_node,
            "errorHandler": data_nodes.error_handler_node,
            "textOverlay": media_nodes.text_overlay_node,
            "imageGenerator": media_nodes.image_generator_node,
            "imageUpload": media_nodes.image_upload_node,
            "socialMedia": social_nodes.social_media_node,
            "instagram_post": social_nodes.instagram_post_node,
        }

    def get_executor(self, node_type: str) -> Callable:
        """Return the callable that can execute the given node type.

        Falls back to ai_agent_node to retain current permissive behavior.
        """
        return self._dispatch.get(node_type, ai_nodes.ai_agent_node)