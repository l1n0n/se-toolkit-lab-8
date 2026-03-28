# ---
# Stage 1: build the application
# ---

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}astral/uv:python3.14-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Copy workspace root files from parent context
COPY --from=workspace pyproject.toml uv.lock ./

# Copy nanobot project
COPY pyproject.toml ./nanobot-pyproject.toml
COPY entrypoint.py ./nanobot-entrypoint.py

# Sync nanobot package only (without workspace)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-workspace --package nanobot

# Copy full source trees from workspace
COPY --from=workspace nanobot/ ./nanobot/
COPY --from=workspace mcp/ ./mcp/
COPY --from=workspace nanobot-websocket-channel/ ./nanobot-websocket-channel/

# Install all packages (not editable)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install ./mcp/mcp-lms ./mcp/mcp-obs ./nanobot-websocket-channel/nanobot-webchat ./nanobot-websocket-channel/mcp-webchat

# ---
# Stage 2: runtime image
# ---

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.14.2-slim-bookworm

ARG APP_UID=1000
ARG APP_GID=1000

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Create app user
RUN groupadd --system --gid ${APP_GID} appgroup \
    && useradd --system --gid ${APP_GID} --uid ${APP_UID} --create-home appuser

# Copy application from builder
COPY --from=builder --chown=appuser:appgroup /app /app

ENV PATH="/app/.venv/bin:$PATH"

USER appuser
WORKDIR /app

CMD ["python", "/app/nanobot/entrypoint.py"]
