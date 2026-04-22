"""LiteLLM-backed gateway (Decision 11, DIR-12.5).

Routes by tier; falls back across providers for resilience.
z.ai is reached via LiteLLM's OpenAI-compatible adapter (z.ai exposes an
OpenAI-shaped endpoint at https://api.z.ai/api/paas/v4 — set api_base + api_key
on each call OR via env vars).
"""
import os
from typing import Any

import litellm

from synthius_mem.config import get_settings
from synthius_mem.llm.models import ModelTier

# Tier → primary model mapping (Decision 11)
_TIER_MODELS: dict[ModelTier, str] = {
    ModelTier.VOLUME: "openai/glm-4.7-flashx",
    ModelTier.QUALITY: "openai/glm-4.6",
    ModelTier.FREE: "openai/glm-4.5-flash",
}

# Fallback chain per tier (Decision 11 trade-off mitigation)
_FALLBACKS: dict[ModelTier, list[str]] = {
    ModelTier.VOLUME: [
        "openai/glm-4.7-flashx",
        "openai/glm-4.5-air",
        "anthropic/claude-haiku-4-5-20251001",
    ],
    ModelTier.QUALITY: [
        "openai/glm-4.6",
        "openai/glm-4.7",
        "anthropic/claude-haiku-4-5-20251001",
    ],
    ModelTier.FREE: [
        "openai/glm-4.5-flash",
        "openai/glm-4.7-flash",
    ],
}


class LLMGateway:
    """Tier-aware LLM gateway with provider fallback.

    All non-test code MUST go through this class — no direct provider SDKs.
    Compliance-checklist item per Decision 11 + DIR-12.5.
    """

    def __init__(self) -> None:
        settings = get_settings()
        if settings.zai_api_key:
            os.environ["OPENAI_API_KEY"] = settings.zai_api_key
            os.environ["OPENAI_API_BASE"] = "https://api.z.ai/api/paas/v4"
        if settings.anthropic_api_key:
            os.environ["ANTHROPIC_API_KEY"] = settings.anthropic_api_key

    @staticmethod
    def model_for(tier: ModelTier) -> str:
        return _TIER_MODELS[tier]

    @staticmethod
    def fallback_chain(tier: ModelTier) -> list[str]:
        return _FALLBACKS[tier]

    def complete(
        self,
        *,
        tier: ModelTier,
        messages: list[dict[str, str]],
        json_mode: bool = False,
        temperature: float = 0.0,
        max_tokens: int = 2048,
    ) -> str:
        """Returns the assistant's content string."""
        kwargs: dict[str, Any] = {  # type: ignore[explicit-any]
            "model": self.model_for(tier),
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "fallbacks": self.fallback_chain(tier)[1:],  # primary excluded
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        resp = litellm.completion(**kwargs)
        return resp.choices[0].message.content  # type: ignore[no-any-return]
