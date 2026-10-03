"""Tests against the real server, started the way a user starts it.

On a new, empty database: `alembic upgrade head`, then `uvicorn
ai_hive_memory.main:app` as a separate process on a free port. The tests
talk to it over HTTP, so they see what a real client sees, including when
a response arrives compared with when its data is committed.

No real LLM is called. The app has no switch for a fake provider, so the
test starts a small OpenAI-compatible server in this process and points
OPENAI_API_BASE at it. This works only while ZAI_API_KEY is empty: the
gateway replaces OPENAI_API_BASE with the z.ai address when that key is set,
so the test sets it to "". HTTP(S)_PROXY point at a closed port, so any
request to a host other than 127.0.0.1 fails instead of reaching a real
provider.

The database server is the one the other integration tests use
(DATABASE_URL); the test creates its own database there and drops it at the
end.
"""
import json
import os
import socket
import subprocess
import sys
import threading
import time
import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import httpx
import pytest
from fastapi import status
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url

from ai_hive_memory.config import get_settings

REPO_ROOT = Path(__file__).resolve().parents[2]
START_TIMEOUT_S = 30.0
DEAD_PROXY = "http://127.0.0.1:9"
PERSONA_ROUNDS = 50
JOB_TIMEOUT_S = 30.0


class _FakeChat(BaseHTTPRequestHandler):
    """Answers every chat completion with the JSON object `{}`."""

    calls = 0

    def do_POST(self) -> None:
        self.rfile.read(int(self.headers.get("content-length", "0")))
        type(self).calls += 1
        body = json.dumps({
            "id": "fake", "object": "chat.completion", "created": int(time.time()),
            "model": "fake",
            "choices": [{
                "index": 0, "finish_reason": "stop",
                "message": {"role": "assistant", "content": "{}"},
            }],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        }).encode()
        self.send_response(status.HTTP_200_OK)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        pass


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port: int = s.getsockname()[1]
        return port


@pytest.fixture
def fresh_database() -> Iterator[tuple[URL, URL]]:
    """Create an empty database; yield (owner URL, app URL); drop it afterwards."""
    owner = make_url(get_settings().database_url)
    name = f"smoke_{uuid.uuid4().hex[:12]}"
    admin = create_engine(owner, isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        conn.execute(text(f'CREATE DATABASE "{name}"'))
    app = make_url(get_settings().app_database_url).set(database=name)
    try:
        yield owner.set(database=name), app
    finally:
        with admin.connect() as conn:
            conn.execute(text(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))
        admin.dispose()


@pytest.fixture
def fake_llm() -> Iterator[str]:
    """Run the fake chat server; yield its base URL."""
    _FakeChat.calls = 0
    server = ThreadingHTTPServer(("127.0.0.1", 0), _FakeChat)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}/v1"
    finally:
        server.shutdown()
        server.server_close()


def _env(owner: URL, app: URL, llm_base: str) -> dict[str, str]:
    env = dict(os.environ)
    env.update({
        "DATABASE_URL": owner.render_as_string(hide_password=False),
        "APP_DATABASE_URL": app.render_as_string(hide_password=False),
        "JWT_SECRET": "startup-smoke-test",
        "ZAI_API_KEY": "",
        "ANTHROPIC_API_KEY": "",
        "OPENAI_API_KEY": "fake",
        "OPENAI_API_BASE": llm_base,
        "LITELLM_LOCAL_MODEL_COST_MAP": "True",
        "HTTPS_PROXY": DEAD_PROXY,
        "HTTP_PROXY": DEAD_PROXY,
        "NO_PROXY": "127.0.0.1,localhost",
    })
    return env


def _wait_healthy(client: httpx.Client, proc: subprocess.Popen[bytes], log: Path) -> None:
    deadline = time.monotonic() + START_TIMEOUT_S
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            pytest.fail(f"server exited with {proc.returncode}:\n{log.read_text()[-4000:]}")
        try:
            if client.get("/health").status_code == status.HTTP_200_OK:
                return
        except httpx.TransportError:
            pass
        time.sleep(0.2)
    pytest.fail(f"server did not answer /health in {START_TIMEOUT_S} s:\n"
                f"{log.read_text()[-4000:]}")


@dataclass
class LiveServer:
    client: httpx.Client
    log: Path


@pytest.fixture
def live_server(
    fresh_database: tuple[URL, URL], fake_llm: str, tmp_path: Path,
) -> Iterator[LiveServer]:
    """Migrate the fresh database, start uvicorn on it, yield a client."""
    owner, app = fresh_database
    env = _env(owner, app, fake_llm)

    migrate = subprocess.run(
        [sys.executable, "-m", "alembic", "-c", str(REPO_ROOT / "alembic.ini"),
         "upgrade", "head"],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=120, check=False,
    )
    assert migrate.returncode == 0, migrate.stdout + migrate.stderr

    port = _free_port()
    log = tmp_path / "server.log"
    with log.open("wb") as out:
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "ai_hive_memory.main:app",
             "--host", "127.0.0.1", "--port", str(port)],
            cwd=tmp_path, env=env, stdout=out, stderr=subprocess.STDOUT,
        )
    try:
        with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=10,
                          trust_env=False) as client:
            _wait_healthy(client, proc, log)
            yield LiveServer(client=client, log=log)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=10)


def _signup(client: httpx.Client) -> dict[str, str]:
    signup = client.post("/signup", json={
        "subject": "live@test", "tos_version": "2026-04-21-mvp",
        "scope_attestation": {
            "no_phi": True, "no_payment_data": True, "no_minors": True,
            "no_eu_uk_residents": True, "no_sensitive_categories": True,
        },
    })
    assert signup.status_code == status.HTTP_200_OK, signup.text
    return {"Authorization": f"Bearer {signup.json()['access_token']}"}


def test_created_persona_is_visible_to_the_next_request(live_server: LiveServer) -> None:
    """A client that gets 201 for a persona can use it in its very next request."""
    client = live_server.client
    auth = _signup(client)
    missing = 0
    for _ in range(PERSONA_ROUNDS):
        created = client.post("/personas", headers=auth)
        assert created.status_code == status.HTTP_201_CREATED, created.text
        listed = client.get("/personas", headers=auth)
        assert listed.status_code == status.HTTP_200_OK, listed.text
        if created.json()["persona_id"] not in listed.json()["personas"]:
            missing += 1
    assert missing == 0, (
        f"{missing} of {PERSONA_ROUNDS} personas were missing from the request "
        "right after their 201"
    )


def test_upload_is_ingested_with_the_fake_llm(live_server: LiveServer) -> None:
    """The main user path: signup, persona, WhatsApp upload, job DONE."""
    client = live_server.client
    assert client.get("/openapi.json").status_code == status.HTTP_200_OK
    auth = _signup(client)
    persona = client.post("/personas", headers=auth)
    assert persona.status_code == status.HTTP_201_CREATED, persona.text

    upload = client.post(
        f"/personas/{persona.json()['persona_id']}/conversations", headers=auth,
        json={"format": "whatsapp", "content": "[2026-04-21 12:00] Alice: I work at Acme\n"},
    )
    assert upload.status_code == status.HTTP_202_ACCEPTED, upload.text
    job_id = upload.json()["job_id"]

    deadline = time.monotonic() + JOB_TIMEOUT_S
    job = client.get(f"/jobs/{job_id}", headers=auth)
    while job.status_code == status.HTTP_200_OK and job.json()["status"] in {
        "PENDING", "RUNNING",
    }:
        assert time.monotonic() < deadline, f"job not finished: {job.text}"
        time.sleep(0.2)
        job = client.get(f"/jobs/{job_id}", headers=auth)
    assert job.status_code == status.HTTP_200_OK, job.text
    assert job.json()["status"] == "DONE", (
        f"{job.text}\n{live_server.log.read_text()[-4000:]}"
    )
    assert _FakeChat.calls > 0, "the job finished without asking the LLM"
