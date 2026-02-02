"""
Environment-based configuration for SentinelVision backend.
Configurable thresholds for risk verdict and model settings.
"""
from functools import lru_cache
from typing import Dict

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "SentinelVision"
    debug: bool = False

    # Thresholds for risk verdict (0.0 - 1.0)
    # BLOCK: any category above this → BLOCK
    threshold_block: float = 0.85
    # REVIEW: any category above this but below block → REVIEW
    threshold_review: float = 0.45
    # Below review → SAFE

    # Per-category overrides (optional): category_name -> block threshold
    # If set, that category uses its own block threshold for verdict
    category_block_overrides: str = ""  # e.g. "sexual_content:0.7,violence:0.8"

    # Model settings
    clip_model_id: str = "openai/clip-vit-base-patch32"
    caption_model_id: str = "Salesforce/blip-image-captioning-base"
    device: str = "cpu"  # "cuda" or "cpu"

    # API
    max_upload_mb: int = 10
    allowed_content_types: tuple = ("image/jpeg", "image/png", "image/webp")

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024

    def get_category_overrides(self) -> Dict[str, float]:
        """Parse category_block_overrides into a dict."""
        out = {}
        for part in self.category_block_overrides.strip().split(","):
            part = part.strip()
            if not part:
                continue
            if ":" in part:
                name, val = part.split(":", 1)
                try:
                    out[name.strip().lower().replace(" ", "_")] = float(val.strip())
                except ValueError:
                    pass
        return out


@lru_cache
def get_settings() -> Settings:
    return Settings()
