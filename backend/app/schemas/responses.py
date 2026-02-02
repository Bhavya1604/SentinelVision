"""
Structured response schemas for the SentinelVision API.
"""
from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class RiskVerdict(str, Enum):
    """Overall risk verdict for the image."""

    SAFE = "SAFE"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


class CategoryScore(BaseModel):
    """Confidence score for a single moderation category."""

    category: str = Field(..., description="Category name (e.g. nsfw, violence)")
    score: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    label: str = Field(..., description="Human-readable label")


class AnalyzeImageResponse(BaseModel):
    """Response for POST /analyze-image."""

    verdict: RiskVerdict = Field(..., description="Overall risk verdict")
    verdict_reason: str = Field(
        ..., description="Short explanation of why this verdict was chosen"
    )
    categories: List[CategoryScore] = Field(
        ..., description="Confidence score per moderation category"
    )
    description: str = Field(
        ..., description="Natural-language image description for explainability"
    )
    image_id: str | None = Field(
        default=None, description="Optional client-provided image identifier"
    )

    model_config = {"json_schema_extra": {"example": None}}  # Set in __init__.py or here
