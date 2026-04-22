"""SP-0.1: real-API spike — verify GLM-4.7-FlashX returns parseable JSON
that round-trips through a closed Pydantic schema with additionalProperties:false.

Skip without ZAI_API_KEY env var. Mark as @pytest.mark.real_api.
"""
import json
import os

import pytest
from pydantic import BaseModel, ConfigDict

from synthius_mem.llm.gateway import LLMGateway  # type: ignore[import-untyped]
from synthius_mem.llm.models import ModelTier  # type: ignore[import-untyped]


class Person(BaseModel):  # type: ignore[explicit-any]
    model_config = ConfigDict(extra="forbid")
    name: str
    age: int
    occupation: str


@pytest.mark.real_api
@pytest.mark.skipif(not os.getenv("ZAI_API_KEY"), reason="ZAI_API_KEY not set")
def test_glm_47_flashx_returns_closed_schema_compatible_json() -> None:
    gw = LLMGateway()
    schema_hint = json.dumps(Person.model_json_schema(), indent=2)
    raw = gw.complete(
        tier=ModelTier.VOLUME,
        messages=[
            {
                "role": "system",
                "content": (
                    "Return ONLY a JSON object matching this schema, "
                    "with NO extra fields:\n" + schema_hint
                ),
            },
            {
                "role": "user",
                "content": "Extract a person from: Alice is a 32yo data scientist.",
            },
        ],
        json_mode=True,
    )
    # Parse + validate — extra fields will be rejected
    data = json.loads(raw)
    person = Person.model_validate(data)
    assert person.name.lower().startswith("alice")
    assert person.age == 32  # noqa: PLR2004 — semantic value from prompt
