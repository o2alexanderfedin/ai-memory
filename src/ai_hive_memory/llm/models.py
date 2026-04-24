"""Model tier enum (Decision 11)."""
from enum import StrEnum


class ModelTier(StrEnum):
    """Three LiteLLM-routed tiers per Decision 11.

    VOLUME  = GLM-4.7-FlashX  ($0.07/$0.40 per M) — extraction, planner, summarizer
    QUALITY = GLM-4.6         ($0.60/$2.20 per M) — psychometric scoring, conflict resolver
    FREE    = GLM-4.5-Flash   (free tier)         — dev, CI, low-stakes
    """

    VOLUME = "volume"
    QUALITY = "quality"
    FREE = "free"
