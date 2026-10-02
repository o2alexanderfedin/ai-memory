"""Wait for an ingest job's background pipeline to end, without polling."""
import threading
from collections.abc import Callable

from fastapi import status
from fastapi.testclient import TestClient

DrivePipeline = Callable[[str, str, str, str, bytes], None]
WaitDone = Callable[[TestClient, str, str], None]
WaitEnded = Callable[[TestClient, str, str], dict[str, object]]

# Only stops a hung pipeline from hanging the test run. A job that ends is
# seen the moment it ends, however long it took; no test waits for this.
_HANG_GUARD_S = 60.0


class JobCompletion:
    """Tells a test when the background pipeline of an ingest job has ended.

    The pipeline itself signals its end, so the wait depends on the job, not
    on a polling budget or on the test client running background tasks before
    it returns the response.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._ended: dict[str, threading.Event] = {}

    def _event(self, job_id: str) -> threading.Event:
        with self._lock:
            return self._ended.setdefault(job_id, threading.Event())

    def wrap(self, drive: DrivePipeline) -> DrivePipeline:
        """Return `drive`, signalling the job's end whether it succeeds or raises."""
        def _drive(tenant_id: str, persona_id: str, job_id: str,
                   fmt: str, raw: bytes) -> None:
            try:
                drive(tenant_id, persona_id, job_id, fmt, raw)
            finally:
                self._event(job_id).set()
        return _drive

    def wait_ended(self, client: TestClient, token: str, job_id: str) -> dict[str, object]:
        """Block until the job's pipeline has ended; return the job as GET /jobs shows it."""
        if not self._event(job_id).wait(_HANG_GUARD_S):
            raise AssertionError(f"pipeline of job {job_id} never ended")
        resp = client.get(f"/jobs/{job_id}", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == status.HTTP_200_OK, resp.text
        body: dict[str, object] = resp.json()
        return body

    def wait_done(self, client: TestClient, token: str, job_id: str) -> None:
        """Block until the job's pipeline has ended, then require status DONE."""
        body = self.wait_ended(client, token, job_id)
        assert body["status"] == "DONE", (
            f"job {job_id} ended as {body['status']}: {body['error']}"
        )
