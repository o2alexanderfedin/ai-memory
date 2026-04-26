"""POST /personas/{persona_id}/conversations — async ingest kickoff (US-2.1, US-2.8)."""
import asyncio
from collections.abc import Generator
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import text
from sqlalchemy.engine import Connection

from ai_hive_memory.auth.deps import CurrentTenant
from ai_hive_memory.ingest.pipeline import IngestPipeline
from ai_hive_memory.llm.gateway import LLMGateway
from ai_hive_memory.storage.connection import request_scoped_conn
from ai_hive_memory.storage.ingest_repository import IngestJobRepository

router = APIRouter()
SUPPORTED_FORMATS = {"whatsapp", "telegram", "pdf", "email", "voice"}


class CreateConversationRequest(BaseModel):  # type: ignore[explicit-any]
    model_config = ConfigDict(extra="forbid")
    format: str
    content: str  # adapter raw input as a string (utf-8-encoded by handler)


class CreateConversationResponse(BaseModel):  # type: ignore[explicit-any]
    model_config = ConfigDict(extra="forbid")
    job_id: str


def _conn_for(claims: CurrentTenant) -> Generator[Connection, None, None]:
    yield from request_scoped_conn(claims.tenant_id)


def _drive_pipeline(tenant_id: str, persona_id: str, job_id: str,
                    fmt: str, raw: bytes) -> None:
    """Background task — opens its OWN connection (FastAPI's request conn is gone)."""
    pipeline = IngestPipeline(gateway=LLMGateway())
    gen = request_scoped_conn(tenant_id)
    bg_conn = next(gen)
    try:
        asyncio.run(pipeline.run(
            conn=bg_conn, tenant_id=tenant_id, persona_id=persona_id,
            job_id=job_id, fmt=fmt, raw=raw,
        ))
    finally:
        gen.close()


@router.post(
    "/personas/{persona_id}/conversations",
    status_code=status.HTTP_202_ACCEPTED,
)
def create_conversation(
    persona_id: str,
    req: CreateConversationRequest,
    background: BackgroundTasks,
    claims: CurrentTenant,
    conn: Annotated[Connection, Depends(_conn_for)],
) -> CreateConversationResponse:
    if req.format not in SUPPORTED_FORMATS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            f"unknown format: {req.format}")
    # Persona must exist under current tenant (RLS-scoped).
    row = conn.execute(
        text("SELECT 1 FROM personas WHERE persona_id = :pid"),
        {"pid": persona_id},
    ).fetchone()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "persona not found")

    # Create the job in its OWN committed transaction so the background task
    # can read it immediately (background tasks run before the request-scoped
    # connection commits under Starlette's AnyIO transport).
    job_gen = request_scoped_conn(claims.tenant_id)
    job_conn = next(job_gen)
    try:
        job_id = IngestJobRepository().create_job(
            job_conn, claims.tenant_id, persona_id, fmt=req.format,
        )
    finally:
        job_gen.close()  # commits the INSERT immediately

    raw = req.content.encode("utf-8")
    background.add_task(
        _drive_pipeline, claims.tenant_id, persona_id, job_id, req.format, raw,
    )
    return CreateConversationResponse(job_id=job_id)
