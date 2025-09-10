FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_NO_INTERACTION=1

WORKDIR /app

# System deps required for Pillow (and general builds)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    libjpeg62-turbo-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry, then resolve deps using the lockfile
RUN pip install --upgrade pip && pip install "poetry>=1.7"

# Copy only dependency files first to leverage Docker cache
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

# Now copy the rest of the source
COPY . .

# Expose port (optional; docker-compose maps it anyway)
EXPOSE 8000

