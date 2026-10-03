"""US-2.8: while the pipeline works, GET /jobs/{id} must show the job RUNNING."""
import json
import threading

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from job_completion import DrivePipeline, WaitDone

from ai_hive_memory.api import conversations
from ai_hive_memory.main import app

client = TestClient(app)

# Only stops a broken test from hanging the run; no test waits for this.
_HANG_GUARD_S = 60.0


class _BlockingGateway:
    """Fake LLM that holds every call until the test releases it."""

    def __init__(self) -> None:
        self.extracting = threading.Event()
        self.release = threading.Event()

    def complete(self, *, tier: object, messages: list[dict[str, str]],
                 json_mode: bool, temperature: float = 0.0,
                 max_tokens: int = 2048) -> str:
        self.extracting.set()
        if not self.release.wait(_HANG_GUARD_S):
            raise AssertionError("test never released the blocked LLM call")
        return json.dumps({})


def _signup() -> str:
    resp = client.post("/signup", json={
        "subject": "u@test",
        "tos_version": "2026-04-21-mvp",
        "scope_attestation": {
            "no_phi": True, "no_payment_data": True, "no_minors": True,
            "no_eu_uk_residents": True, "no_sensitive_categories": True,
        },
    })
    token: str = resp.json()["access_token"]
    return token


def test_job_is_running_while_the_pipeline_works(
    monkeypatch: pytest.MonkeyPatch, wait_done: WaitDone,
) -> None:
    gw = _BlockingGateway()
    monkeypatch.setattr(conversations, "LLMGateway", lambda: gw)
    started: list[str] = []
    drive: DrivePipeline = conversations._drive_pipeline  # already signals the job's end

    def _record_job(tenant_id: str, persona_id: str, job_id: str,
                    fmt: str, raw: bytes) -> None:
        started.append(job_id)
        drive(tenant_id, persona_id, job_id, fmt, raw)

    monkeypatch.setattr(conversations, "_drive_pipeline", _record_job)

    token = _signup()
    auth = {"Authorization": f"Bearer {token}"}
    persona_id = client.post("/personas", headers=auth).json()["persona_id"]
    # The test client runs the background pipeline before the POST returns,
    # so the upload goes in its own thread and this thread plays the client.
    upload = threading.Thread(target=lambda: client.post(
        f"/personas/{persona_id}/conversations", headers=auth,
        json={"format": "whatsapp", "content": "[2026-04-21 12:00] Alice: Hi!\n"},
    ))
    upload.start()
    try:
        assert gw.extracting.wait(_HANG_GUARD_S), "the pipeline never called the LLM"
        (job_id,) = started
        resp = client.get(f"/jobs/{job_id}", headers=auth)
        assert resp.status_code == status.HTTP_200_OK, resp.text
        seen = resp.json()["status"]
    finally:
        gw.release.set()
        upload.join(_HANG_GUARD_S)
    assert seen == "RUNNING", f"while the pipeline works, the client sees the job {seen}"
    wait_done(client, token, job_id)
