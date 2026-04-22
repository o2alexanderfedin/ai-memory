"""FastAPI app entrypoint."""
from fastapi import FastAPI

from synthius_mem.api import auth_routes, health
from synthius_mem.auth.deps import CurrentTenant

app = FastAPI(title="Synthius-Mem", version="0.0.1")

app.include_router(health.router)
app.include_router(auth_routes.router)


@app.get("/personas")
def list_personas(claims: CurrentTenant) -> dict[str, list[str] | str]:
    """Stub — Epic 1 implements this fully."""
    return {"personas": [], "tenant_id": claims.tenant_id}
