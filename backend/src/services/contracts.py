from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ContentV1(BaseModel):
    """Canonical content contract for Instagram/text-based content.
    Fields are optional with defaults to keep downstream robust.
    """

    headline: str = ""
    subhead: str = ""
    bullets: List[str] = Field(default_factory=list)
    caption: str = ""
    hashtags: List[str] = Field(default_factory=list)
    # Optional template hints
    recommended_template: Optional[str] = None
    template_reason: Optional[str] = None


ALIASES: Dict[str, List[str]] = {
    "headline": ["headline", "title", "main_title", "hero"],
    "subhead": ["subhead", "subtitle", "description", "summary"],
    "bullets": ["bullets", "bullet_points", "key_points", "points", "list"],
    "caption": ["caption", "description", "summary", "body"],
    "hashtags": ["hashtags", "tags"],
}


def normalize_to_content_v1(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize arbitrary payload keys to the ContentV1 canonical schema.
    - Applies alias mapping
    - Ensures bullets/hashtags are lists of strings
    - Coerces primitive values to strings
    """
    if not isinstance(payload, dict):
        return {
            "headline": str(payload) if payload is not None else "",
            "subhead": "",
            "bullets": [],
            "caption": str(payload) if payload is not None else "",
            "hashtags": [],
        }

    normalized: Dict[str, Any] = {}

    for canonical, keys in ALIASES.items():
        value = None
        for k in keys:
            if k in payload and payload[k] not in (None, ""):
                value = payload[k]
                break
        if canonical in ("bullets", "hashtags"):
            if isinstance(value, list):
                normalized[canonical] = [str(v).strip() for v in value if v is not None and str(v).strip()]
            elif isinstance(value, str) and value.strip():
                # split on commas or newlines heuristically
                parts = [p.strip() for p in value.replace("\n", ",").split(",")]
                normalized[canonical] = [p for p in parts if p]
            else:
                normalized[canonical] = []
        else:
            normalized[canonical] = str(value).strip() if value is not None else ""

    # Pass-through template hints when present
    for hint in ("recommended_template", "template_reason"):
        if hint in payload:
            normalized[hint] = payload.get(hint)

    return normalized

class EmailInputV1(BaseModel):
    to: str = ""
    subject: str = ""
    body: str = ""


class EmailOutputV1(BaseModel):
    message_id: Optional[str] = None
    status: str = "sent"
    sent_at: str
    provider_meta: Dict[str, Any] = Field(default_factory=dict)


class SlackInputV1(BaseModel):
    channel: str = ""
    message: str = ""


class SlackOutputV1(BaseModel):
    message_ts: Optional[str] = None
    status: str = "sent"
    sent_at: str
    provider_meta: Dict[str, Any] = Field(default_factory=dict)


class ImageUploadInputV1(BaseModel):
    image_data_url: Optional[str] = None
    image_url: Optional[str] = None
    carousel_images: Optional[List[Any]] = None


class ImageUploadOutputV1(BaseModel):
    public_url: str
    public_id: Optional[str] = None
    version: Optional[str] = None
    provider: str = "cloudinary"


class CanvaTemplateInputV1(BaseModel):
    template_id: str
    content: Dict[str, Any]
    export_format: str = "png"
    export_width: int = 1080
    export_height: int = 1080


class CanvaTemplateOutputV1(BaseModel):
    canva_design_id: Optional[str] = None
    canva_design_url: Optional[str] = None
    image_data_url: str


class DataNodeInputV1(BaseModel):
    input_source: Optional[str] = None
    output_name: str = "post_data"
    operation: str = "pass_through"  # pass_through|transform|filter|aggregate
    filter_criteria: Dict[str, Any] = Field(default_factory=dict)
    aggregation_type: str = "sum"


class DataNodeOutputV1(BaseModel):
    output_name: str
    value: Any


class ConditionInputV1(BaseModel):
    condition: str = ""
    input_value: Any = None


class ConditionOutputV1(BaseModel):
    condition_result: bool
    next_step: Optional[str] = None


class DelayInputV1(BaseModel):
    delay_seconds: int = 1


class DelayOutputV1(BaseModel):
    scheduled_for: str


class ScheduleInputV1(BaseModel):
    schedule_type: str = "daily"
    schedule_time: str = "09:00"


class ScheduleOutputV1(BaseModel):
    type: str
    time: str
    created_at: str


class BlogWriterInputV1(BaseModel):
    topic: str
    style: str = "professional"
    length: str = "medium"


class BlogWriterOutputV1(BaseModel):
    topic: str
    content: str
    style: str
    length: str
    generated_at: str


class SeoOptimizerInputV1(BaseModel):
    content: str
    target_keywords: List[str] = Field(default_factory=list)


class SeoOptimizerOutputV1(BaseModel):
    original_content: str
    optimized_content: str
    target_keywords: List[str]
    optimized_at: str


class TextOverlayInputV1(BaseModel):
    structured_data: Dict[str, Any]
    image_url: Optional[str] = None
    image_width: int = 1080
    image_height: int = 1080
    platform: str = "instagram"
    post_type: str = "single"
    use_instagram_template: bool = True
    instagram_template_name: Optional[str] = None
    use_canva_template: bool = False
    canva_template_id: Optional[str] = None


class TextOverlayOutputV1(BaseModel):
    image_url: Optional[str] = None
    image_data_url: Optional[str] = None
    carousel_images: Optional[List[Dict[str, Any]]] = None
    template_used: Optional[str] = None
    platform_used: str
    post_type: str
    status: str = "completed"
    timestamp: str

