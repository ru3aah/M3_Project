FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_NO_INTERACTION=1

WORKDIR /app

# Runtime libs for Pillow (no compilers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Poetry
RUN pip install --upgrade pip && pip install "poetry>=1.7"

# Install only main deps first for caching
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --only main

# App source
COPY . .

EXPOSE 8000