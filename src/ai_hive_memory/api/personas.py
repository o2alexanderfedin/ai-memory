"""POST + GET /personas — onboard + list personas under the current tenant scope (S-1)."""
from collections.abc import Generator
from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.engine import Connection

from ai_hive_memory.auth.deps import CurrentTenant
from ai_hive_memory.storage.connection import request_scoped_conn
from ai_hive_memory.storage.repository import PersonaRepository

router = APIRouter()
_repo = PersonaRepository()


class CreatePersonaResponse(BaseModel):  # type: ignore[explicit-any]
    model_config = ConfigDict(extra="forbid")
    persona_id: str


class ListPersonasResponse(BaseModel):  # type: ignore[explicit-any]
    model_config = ConfigDict(extra="forbid")
    personas: list[str]


def _conn_for(claims: CurrentTenant) -> Generator[Connection, None, None]:
    """Inline FastAPI dependency: yield a request-scoped Connection for the caller's tenant."""
    yield from request_scoped_conn(claims.tenant_id)


@router.post("/personas", status_code=status.HTTP_201_CREATED)
def create_persona(
    claims: CurrentTenant,
    conn: Annotated[Connection, Depends(_conn_for)],
) -> CreatePersonaResponse:
    persona_id = _repo.create_persona(conn, claims.tenant_id)
    return CreatePersonaResponse(persona_id=persona_id)


@router.get("/personas")
def list_personas(
    claims: CurrentTenant,  # used by Depends(_conn_for) for tenant scoping
    conn: Annotated[Connection, Depends(_conn_for)],
) -> ListPersonasResponse:
    return ListPersonasResponse(personas=_repo.list_personas(conn))
