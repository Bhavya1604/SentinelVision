"""
ML inference layer: multi-label moderation (CLIP zero-shot) and image captioning (BLIP).
Lazy-loads models for production efficiency.
"""
from __future__ import annotations

import io
import logging
import math
from typing import Dict

import torch
from PIL import Image

from app.config import get_settings

logger = logging.getLogger(__name__)

# Moderation categories and CLIP text prompts for zero-shot scoring
MODERATION_CATEGORIES: Dict[str, str] = {
    "nsfw": "NSFW or adult content",
    "violence": "violence, blood, or gore",
    "sexual_content": "sexual or suggestive content",
    "hate_symbols": "hate symbols or extremist imagery",
    "drugs": "drugs or drug paraphernalia",
    "self_harm": "self-harm or suicide-related content",
}

HUMAN_LABELS: Dict[str, str] = {
    "nsfw": "NSFW",
    "violence": "Violence",
    "sexual_content": "Sexual content",
    "hate_symbols": "Hate symbols",
    "drugs": "Drugs",
    "self_harm": "Self-harm",
}

# Per-category score calibration (independent binary signal per category).
# CLIP cosine similarity for this model: safe images often ~0.20-0.26, risky ~0.30+.
# BASELINE_SIM set so typical safe sim maps to ~0.05-0.20; SIM_SCALE so strong evidence rises.
BASELINE_SIM = 0.27
SIM_SCALE = 55.0


class InferenceService:
    """
    Handles image moderation (CLIP zero-shot) and captioning (BLIP).
    Models are loaded on first use.
    """

    _clip_processor = None
    _clip_model = None
    _caption_processor = None
    _caption_model = None

    def __init__(self) -> None:
        self._settings = get_settings()
        self._device = self._get_device()

    def _get_device(self) -> torch.device:
        if self._settings.device == "cuda" and torch.cuda.is_available():
            return torch.device("cuda")
        return torch.device("cpu")

    def _load_clip(self) -> tuple:
        if InferenceService._clip_model is not None:
            return InferenceService._clip_processor, InferenceService._clip_model
        from transformers import CLIPProcessor, CLIPModel

        logger.info("Loading CLIP model: %s", self._settings.clip_model_id)
        processor = CLIPProcessor.from_pretrained(self._settings.clip_model_id)
        model = CLIPModel.from_pretrained(self._settings.clip_model_id)
        model = model.to(self._device)  # type: ignore[arg-type]
        model.eval()
        InferenceService._clip_processor = processor
        InferenceService._clip_model = model
        return processor, model

    def _load_caption(self) -> tuple:
        if InferenceService._caption_model is not None:
            return InferenceService._caption_processor, InferenceService._caption_model
        from transformers import BlipProcessor, BlipForConditionalGeneration

        logger.info("Loading BLIP caption model: %s", self._settings.caption_model_id)
        processor = BlipProcessor.from_pretrained(self._settings.caption_model_id)
        model = BlipForConditionalGeneration.from_pretrained(
            self._settings.caption_model_id
        )
        model = model.to(self._device)  # type: ignore[arg-type]
        model.eval()
        InferenceService._caption_processor = processor
        InferenceService._caption_model = model
        return processor, model

    def run_moderation(self, image: Image.Image) -> Dict[str, float]:
        """
        Run multi-label moderation using CLIP zero-shot.
        Each category is an independent binary signal: per-category cosine
        similarity is mapped with a conservative sigmoid so safe images
        (similarity ~0.22-0.30) produce low scores (0.05-0.20); only strong
        visual evidence (high similarity) produces high scores.
        No softmax or normalization across categories.
        Returns dict of category -> score in [0, 1].
        """
        processor, model = self._load_clip()
        texts = [MODERATION_CATEGORIES[cat] for cat in MODERATION_CATEGORIES]
        inputs = processor(
            text=texts,
            images=image,
            return_tensors="pt",
            padding=True,
            truncation=True,
        ).to(self._device)
        with torch.no_grad():
            outputs = model(**inputs)
            image_emb = outputs.image_embeds
            text_emb = outputs.text_embeds
            image_emb = image_emb / image_emb.norm(dim=-1, keepdim=True)
            text_emb = text_emb / text_emb.norm(dim=-1, keepdim=True)
            # Cosine similarity per category (independent; no shared distribution)
            sims = (image_emb @ text_emb.T).squeeze(0).cpu()
        # Conservative sigmoid: sim <= BASELINE_SIM -> low score; sim > BASELINE_SIM -> rises
        # Safe images (sim ~0.25-0.30) -> ~0.05-0.20; strong evidence (sim 0.5+) -> high
        # Use math for scalar sigmoid (torch.sigmoid expects Tensor in PyTorch 2.x)
        scores = []
        for i in range(sims.shape[0]):
            x = (sims[i].item() - BASELINE_SIM) * SIM_SCALE
            s = 1.0 / (1.0 + math.exp(-x))
            scores.append(max(0.0, min(1.0, s)))
        return dict(zip(MODERATION_CATEGORIES.keys(), scores))

    def run_caption(self, image: Image.Image) -> str:
        """Generate a short natural-language description of the image."""
        processor, model = self._load_caption()
        inputs = processor(images=image, return_tensors="pt").to(self._device)
        with torch.no_grad():
            out = model.generate(**inputs, max_length=50)
        caption = processor.decode(out[0], skip_special_tokens=True).strip()
        return caption or "No description generated."

    def analyze(self, image_bytes: bytes) -> tuple[Dict[str, float], str]:
        """
        Run full analysis: moderation scores and caption.
        Returns (category_scores, description).
        """
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        scores = self.run_moderation(image)
        description = self.run_caption(image)
        return scores, description


def get_inference_service() -> InferenceService:
    return InferenceService()
