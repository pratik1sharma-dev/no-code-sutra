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

