# docker/backend/Dockerfile

# Stage 1: Builder
FROM python:3.11-slim-bookworm AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
   build-essential \
   gcc \
   && rm -rf /var/lib/apt/lists/*

# Set work directory
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

# Set work directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
   libsqlite3-dev \
   && rm -rf /var/lib/apt/lists/*

# Copy dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY backend/ .

# Copy configuration files
COPY backend/app/config ./config

# Set HF_HOME environment variable (replacing TRANSFORMERS_CACHE)
ENV HF_HOME=/app/.cache/huggingface

# Create the cache directory
RUN mkdir -p /app/.cache/huggingface

# Create non-root user
RUN adduser --disabled-password --no-create-home appuser

# Change ownership of the application directory to appuser
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Create logs directory
RUN mkdir -p /app/logs

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]