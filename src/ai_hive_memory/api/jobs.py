"""GET /jobs/{job_id} — async job status polling (US-2.8)."""
from collections.abc import Generator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.engine import Connection

from ai_hive_memory.auth.deps import CurrentTenant
from ai_hive_memory.storage.connection import request_scoped_conn
from ai_hive_memory.storage.ingest_repository import IngestJobRepository

router = APIRouter()


class JobStatusResponse(BaseModel):  # type: ignore[explicit-any]
    model_config = ConfigDict(extra="forbid")
    job_id: str
    persona_id: str
    format: str
    status: str
    domain_status: dict[str, str]
    error: str | None


def _conn_for(claims: CurrentTenant) -> Generator[Connection, None, None]:
    yield from request_scoped_conn(claims.tenant_id)


@router.get("/jobs/{job_id}")
def get_job(
    job_id: str,
    claims: CurrentTenant,
    conn: Annotated[Connection, Depends(_conn_for)],
) -> JobStatusResponse:
    row = IngestJobRepository().get_job(conn, claims.tenant_id, job_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "job not found")
    return JobStatusResponse(
        job_id=str(row["job_id"]),
        persona_id=row["persona_id"],
        format=row["format"],
        status=row["status"],
        domain_status=row["domain_status"] or {},
        error=row["error"],
    )
