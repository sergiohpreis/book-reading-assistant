# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml .
COPY src/ src/

RUN uv pip install --system --no-cache .

# Development stage
FROM python:3.12-slim AS dev

WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml .
COPY src/ src/

RUN uv pip install --system --no-cache ".[dev]"

ENTRYPOINT ["notes"]

# Production stage
FROM python:3.12-slim AS production

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/notes /usr/local/bin/notes

ENTRYPOINT ["notes"]
