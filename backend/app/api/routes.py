"""
API layer: /analyze-image endpoint with multipart upload and structured responses.
"""
import logging
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.schemas.responses import AnalyzeImageResponse
from app.config import get_settings
from app.services.inference import get_inference_service
from app.services.post_processing import get_post_processing_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["moderation"])


def _validate_upload(file: UploadFile, max_bytes: int, allowed: tuple) -> bytes:
    """Validate content type and size; return file bytes."""
    if file.content_type not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid content type. Allowed: {list(allowed)}",
        )
    content = file.file.read()
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {max_bytes // (1024*1024)} MB",
        )
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file.")
    return content


@router.post(
    "/analyze-image",
    response_model=AnalyzeImageResponse,
    summary="Analyze image for moderation",
    description="Upload an image; returns risk verdict, per-category scores, and a short description.",
)
async def analyze_image(
    file: UploadFile = File(..., description="Image file (JPEG, PNG, WebP)"),
    image_id: Optional[str] = Form(None),
) -> AnalyzeImageResponse:
    """
    Accept multipart image upload, run moderation + captioning, apply policy, return JSON.
    """
    settings = get_settings()
    try:
        raw = _validate_upload(
            file,
            settings.max_upload_bytes,
            settings.allowed_content_types,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Upload validation failed: %s", e)
        raise HTTPException(status_code=400, detail="Invalid upload.") from e

    try:
        inference = get_inference_service()
        post = get_post_processing_service()
    except Exception as e:
        logger.exception("Service initialization failed: %s", e)
        raise HTTPException(
            status_code=503,
            detail="Inference service unavailable.",
        ) from e

    try:
        scores, description = inference.analyze(raw)
    except Exception as e:
        logger.exception("Inference failed: %s", e)
        raise HTTPException(
            status_code=500,
            detail="Image analysis failed. The file may be corrupted or unsupported.",
        ) from e

    verdict, reason = post.compute_verdict(scores)
    categories = post.scores_to_categories(scores)

    return AnalyzeImageResponse(
        verdict=verdict,
        verdict_reason=reason,
        categories=categories,
        description=description,
        image_id=image_id,
    )
