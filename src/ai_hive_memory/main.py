"""FastAPI app entrypoint."""
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from ai_hive_memory.api import auth_routes, conversations, health, index, jobs, personas, signup_routes
from ai_hive_memory.config import get_settings
from ai_hive_memory.observability.otel import setup_tracing

app = FastAPI(title="AI Hive® Memory", version="0.0.1")

setup_tracing(otlp_endpoint=get_settings().otel_exporter_otlp_endpoint or None)
FastAPIInstrumentor.instrument_app(app)

app.include_router(index.router)
app.include_router(health.router)
app.include_router(auth_routes.router)
app.include_router(signup_routes.router)
app.include_router(personas.router)
app.include_router(conversations.router)
app.include_router(jobs.router)
