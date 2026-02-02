"""
Post-processing and policy layer: compute risk verdict from scores and configurable thresholds.
"""
from typing import Dict, List, Tuple

from app.config import get_settings
from app.schemas.responses import CategoryScore, RiskVerdict

from .inference import HUMAN_LABELS


class PostProcessingService:
    """Applies policy rules and thresholds to raw scores."""

    def __init__(self) -> None:
        self._settings = get_settings()

    def _get_block_threshold(self, category: str) -> float:
        overrides = self._settings.get_category_overrides()
        return overrides.get(category, self._settings.threshold_block)

    def compute_verdict(self, scores: Dict[str, float]) -> Tuple[RiskVerdict, str]:
        """
        Compute overall verdict (SAFE / REVIEW / BLOCK) and a short reason.
        Policy: BLOCK if any category >= its block threshold; else REVIEW if any >= review; else SAFE.
        """
        block_th = self._settings.threshold_block
        review_th = self._settings.threshold_review
        block_cats: List[str] = []
        review_cats: List[str] = []
        for cat, score in scores.items():
            cat_block = self._get_block_threshold(cat)
            if score >= cat_block:
                block_cats.append(cat)
            elif score >= review_th:
                review_cats.append(cat)
        if block_cats:
            names = ", ".join(HUMAN_LABELS.get(c, c) for c in block_cats)
            return RiskVerdict.BLOCK, f"Blocked: high confidence in ({names})."
        if review_cats:
            names = ", ".join(HUMAN_LABELS.get(c, c) for c in review_cats)
            return RiskVerdict.REVIEW, f"Flagged for review: ({names}) above review threshold."
        return RiskVerdict.SAFE, "No categories exceeded review threshold."

    def scores_to_categories(self, scores: Dict[str, float]) -> List[CategoryScore]:
        """Convert raw scores dict to list of CategoryScore for API response."""
        return [
            CategoryScore(
                category=cat,
                score=round(score, 4),
                label=HUMAN_LABELS.get(cat, cat),
            )
            for cat, score in scores.items()
        ]


def get_post_processing_service() -> PostProcessingService:
    return PostProcessingService()
