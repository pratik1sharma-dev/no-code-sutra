from typing import Callable, Dict

from .nodes import ai_agent
from .nodes import email as email_node
from .nodes import slack as slack_node
from .nodes import data_node as data_exec
from .nodes import condition as condition_exec
from .nodes import delay as delay_exec
from .nodes import schedule as schedule_exec
from .nodes import blog_writer as blog_exec
from .nodes import social_media as social_exec
from .nodes import image_generator as image_gen_exec
from .nodes import seo_optimizer as seo_exec
from .nodes import text_overlay as text_overlay_exec
from .nodes import image_upload as image_upload_exec
from .nodes import linkedin_post as linkedin_post_exec


class NodeDispatcher:
    """Maps node types to executor callables (SRP/OCP)."""

    def __init__(self) -> None:
        self._dispatch: Dict[str, Callable] = {
            "aiAgent": ai_agent.execute,
            "email": email_node.execute,
            "slack": slack_node.execute,
            "data": data_exec.execute,
            "condition": condition_exec.execute,
            "delay": delay_exec.execute,
            "schedule": schedule_exec.execute,
            "blogWriter": blog_exec.execute,
            "socialMedia": social_exec.execute,
            "instagram_post": social_exec.execute_instagram,
            "linkedin_post": linkedin_post_exec.execute,
            "textOverlay": text_overlay_exec.execute,
            "imageGenerator": image_gen_exec.execute,
            "imageUpload": image_upload_exec.execute,
            "seoOptimizer": seo_exec.execute,
        }

    def get_executor(self, node_type: str) -> Callable:
        return self._dispatch.get(node_type, ai_agent.execute)