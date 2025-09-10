FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# System deps for psycopg2 (libpq) and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Workdir aligned with compose (volumes: .:/app)
WORKDIR /app

# Leverage Docker layer cache: install deps before copying the whole repo
COPY pyproject.toml poetry.lock* /app/
RUN pip install --upgrade pip && pip install "poetry>=1.7" \
  && poetry install --no-root

# Now copy the rest of the project
COPY . /app/

EXPOSE 8000

