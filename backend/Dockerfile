FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY packages/uzum-connector /app/packages/uzum-connector
COPY backend/pyproject.toml /app/backend/pyproject.toml

RUN pip install --upgrade pip && \
    pip install -e /app/packages/uzum-connector && \
    pip install /app/backend

COPY backend /app/backend
WORKDIR /app/backend

EXPOSE 8000
CMD ["python", "-m", "anasklad.granian_entry"]
