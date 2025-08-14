from typing import Callable, Dict

from .langgraph_nodes.workflow_nodes import LangGraphWorkflowNodes


class NodeDispatcher:
	"""Maps node types to executor callables.

	This enables extensibility (OCP) by centralizing the mapping between a
	string node type and the function that can execute that node. The mapping
	can be extended without changing core executor logic.
	"""

	def __init__(self, nodes: LangGraphWorkflowNodes) -> None:
		self._nodes = nodes
		self._dispatch: Dict[str, Callable] = {
			"aiAgent": self._nodes.ai_agent_node,
			"email": self._nodes.email_node,
			"slack": self._nodes.slack_node,
			"data": self._nodes.data_node,
			"condition": self._nodes.condition_node,
			"delay": self._nodes.delay_node,
			"schedule": self._nodes.schedule_node,
			"blogWriter": self._nodes.blog_writer_node,
			"socialMedia": self._nodes.social_media_node,
			"instagram_post": self._nodes.social_media_node,
			"textOverlay": self._nodes.text_overlay_node,
			"imageGenerator": self._nodes.image_generator_node,
			"imageUpload": self._nodes.image_upload_node,
			"seoOptimizer": self._nodes.seo_optimizer_node,
		}

	def get_executor(self, node_type: str) -> Callable:
		"""Return the callable that can execute the given node type.

		Falls back to ai_agent_node to retain current permissive behavior.
		"""
		return self._dispatch.get(node_type, self._nodes.ai_agent_node)