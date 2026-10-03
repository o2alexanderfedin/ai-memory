FROM python:3.12-slim

RUN pip install --no-cache-dir uv

WORKDIR /app
COPY pyproject.toml uv.lock* ./
# Dependencies first (cached layer); the project itself needs src/, so it is
# installed after the copy below.
RUN uv sync --frozen --no-dev --no-install-project

COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./
RUN uv sync --frozen --no-dev

EXPOSE 8000
# --no-sync: everything is installed above; starting must not download
# anything (plain `uv run` would install the dev group from PyPI first).
CMD ["uv", "run", "--no-sync", "uvicorn", "ai_hive_memory.main:app", "--host", "0.0.0.0", "--port", "8000"]
