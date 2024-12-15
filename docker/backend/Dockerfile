# KONSPECTO/docker/backend/Dockerfile

# Stage 1: Builder
FROM python:3.11-slim-bookworm AS builder

# Install build dependencies and FFmpeg with the necessary codecs
RUN apt-get update && apt-get install -y --no-install-recommends \
   build-essential \
   gcc \
   ffmpeg \
   libglib2.0-0 \
   libsm6 \
   libxext6 \
   libavcodec-extra \
   libavdevice-dev \
   libavfilter-dev \
   libavformat-dev \
   libavutil-dev \
   libswscale-dev \
   libmp3lame0 \
   && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Install Poetry
RUN pip install poetry==1.7.1

# Copy dependency files
COPY backend/pyproject.toml backend/poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
   && poetry install --no-interaction --no-ansi --only main

# Stage 2: Production
FROM python:3.11-slim-bookworm

# Install runtime dependencies and FFmpeg with necessary codecs
RUN apt-get update && apt-get install -y --no-install-recommends \
   ffmpeg \
   libglib2.0-0 \
   libsm6 \
   libxext6 \
   libavcodec-extra \
   libavdevice-dev \
   libavfilter-dev \
   libavformat-dev \
   libavutil-dev \
   libswscale-dev \
   libmp3lame0 \
   libsqlite3-dev \
   && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Создание папки для кэша HuggingFace
RUN mkdir -p /app/models/huggingface_cache

# Создание необходимой директории для HuggingFace
RUN mkdir -p /app/.cache/huggingface/hub

# Copy dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY backend/ .

# Copy configuration files
COPY backend/app/config ./config

# Set environment variables for cache location
ENV HF_HOME=/app/.cache/huggingface

# Set environment variable для папки кэша HuggingFace
ENV HUGGINGFACE_CACHE_FOLDER=/app/models/huggingface_cache

# Create unprivileged user (без --no-create-home, так что домашняя директория создается)
RUN adduser --disabled-password appuser

# Изменение владельца рабочей директории и домашней директории
RUN chown -R appuser:appuser /app /home/appuser

# Switch to unprivileged user
USER appuser

# Create logs directory
RUN mkdir -p /app/logs

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
