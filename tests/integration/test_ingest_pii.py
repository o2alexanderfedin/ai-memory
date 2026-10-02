"""US-2.4 + Decision 12: SSN + credit-card patterns are redacted before extractor sees text."""
import json
from unittest.mock import patch

from fastapi.testclient import TestClient
from job_completion import WaitDone

from ai_hive_memory.main import app

client = TestClient(app)


def _signup() -> str:
    return client.post("/signup", json={
        "subject": "u@test",
        "tos_version": "2026-04-21-mvp",
        "scope_attestation": {
            "no_phi": True, "no_payment_data": True, "no_minors": True,
            "no_eu_uk_residents": True, "no_sensitive_categories": True,
        },
    }).json()["access_token"]


def _persona(token: str) -> str:
    return client.post("/personas",
                       headers={"Authorization": f"Bearer {token}"}).json()["persona_id"]


@patch("ai_hive_memory.api.conversations.LLMGateway")
def test_ssn_and_cc_are_redacted_before_extractor_sees_text(
    mock_gw_cls: object, wait_done: WaitDone,
) -> None:
    seen_user_messages: list[str] = []

    def _complete(*, tier: object, messages: list[dict[str, str]],
                  json_mode: bool, temperature: float = 0.0,
                  max_tokens: int = 2048) -> str:
        seen_user_messages.append(messages[1]["content"])
        return json.dumps({})

    mock_gw_cls.return_value.complete.side_effect = _complete  # type: ignore[union-attr]

    token = _signup()
    persona_id = _persona(token)
    content = (
        "[2026-04-21 12:00] Alice: My SSN is 123-45-6789 and card is 4242 4242 4242 4242.\n"
    )
    r = client.post(
        f"/personas/{persona_id}/conversations",
        headers={"Authorization": f"Bearer {token}"},
        json={"format": "whatsapp", "content": content},
    )
    job_id = r.json()["job_id"]
    wait_done(client, token, job_id)

    combined = "\n".join(seen_user_messages)
    assert "[REDACTED-SSN]" in combined
    assert "[REDACTED-CC]" in combined
    assert "123-45-6789" not in combined
    assert "4242 4242 4242 4242" not in combined
