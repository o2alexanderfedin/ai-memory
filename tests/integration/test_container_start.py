"""The Docker image starts and answers /health with no network access.

The image is built from the repository's Dockerfile and started with its own
CMD, on a container with no network at all (`--network none`). /health needs
no database, so the only thing this checks is that the service inside the
image can start by itself: the application must already be installed in the
image, and starting it must not download anything.

Skipped when Docker is not available.
"""
import shutil
import subprocess
import time
import uuid
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_TIMEOUT_S = 900
START_TIMEOUT_S = 90

_HEALTH_PROBE = (
    "import urllib.request, sys; "
    "r = urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2); "
    "sys.exit(0 if r.status == 200 else 1)"
)


def _docker_available() -> bool:
    if shutil.which("docker") is None:
        return False
    probe = subprocess.run(
        ["docker", "info"], capture_output=True, timeout=30, check=False,
    )
    return probe.returncode == 0


def _docker(*args: str, timeout: float = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", *args], capture_output=True, text=True, timeout=timeout, check=False,
    )


@pytest.mark.skipif(not _docker_available(), reason="Docker is not available")
def test_image_serves_health_without_network() -> None:
    suffix = uuid.uuid4().hex[:12]
    tag = f"ai-hive-memory-test:{suffix}"
    name = f"ai-hive-memory-test-{suffix}"
    built = _docker("build", "-t", tag, str(REPO_ROOT), timeout=BUILD_TIMEOUT_S)
    assert built.returncode == 0, built.stdout[-4000:] + built.stderr[-4000:]
    try:
        started = _docker("run", "-d", "--network", "none", "--name", name, tag)
        assert started.returncode == 0, started.stderr
        deadline = time.monotonic() + START_TIMEOUT_S
        healthy = False
        while time.monotonic() < deadline:
            running = _docker("inspect", "-f", "{{.State.Running}}", name)
            if running.stdout.strip() != "true":
                break
            probe = _docker("exec", name, "python", "-c", _HEALTH_PROBE, timeout=30)
            if probe.returncode == 0:
                healthy = True
                break
            time.sleep(1)
        logs = _docker("logs", name)
        assert healthy, (
            "service in the image did not answer /health without network; "
            f"container output:\n{logs.stdout[-4000:]}{logs.stderr[-4000:]}"
        )
    finally:
        _docker("rm", "-f", name)
        _docker("rmi", tag)
