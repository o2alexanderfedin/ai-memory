"""Unit tests for LLMGateway (mocked LiteLLM)."""
from unittest.mock import MagicMock, patch

from ai_hive_memory.llm.gateway import LLMGateway
from ai_hive_memory.llm.models import ModelTier


def test_volume_tier_routes_to_glm_47_flashx() -> None:
    gw = LLMGateway()
    assert gw.model_for(ModelTier.VOLUME) == "openai/glm-4.7-flashx"


def test_quality_tier_routes_to_glm_46() -> None:
    gw = LLMGateway()
    assert gw.model_for(ModelTier.QUALITY) == "openai/glm-4.6"


def test_free_tier_routes_to_glm_45_flash() -> None:
    gw = LLMGateway()
    assert gw.model_for(ModelTier.FREE) == "openai/glm-4.5-flash"


def test_fallback_chain_includes_anthropic() -> None:
    gw = LLMGateway()
    assert "anthropic/claude-haiku-4-5-20251001" in gw.fallback_chain(ModelTier.VOLUME)


@patch("ai_hive_memory.llm.gateway.litellm.completion")
def test_complete_calls_litellm_with_json_object_response_format(
    mock_completion: MagicMock,
) -> None:
    mock_completion.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content='{"x": 1}'))]
    )
    gw = LLMGateway()
    result = gw.complete(
        tier=ModelTier.VOLUME,
        messages=[{"role": "user", "content": "hi"}],
        json_mode=True,
    )
    assert result == '{"x": 1}'
    call_kwargs = mock_completion.call_args.kwargs
    assert call_kwargs["response_format"] == {"type": "json_object"}
    assert call_kwargs["model"] == "openai/glm-4.7-flashx"
