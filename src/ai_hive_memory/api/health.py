"""Health endpoint (DIR-7.2 op #8)."""
from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

_NO_CACHE_HEADERS = {
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "Pragma": "no-cache",
    "Expires": "0",
}


@router.get("/health")
def health() -> JSONResponse:
    body = {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return JSONResponse(content=body, headers=_NO_CACHE_HEADERS)
