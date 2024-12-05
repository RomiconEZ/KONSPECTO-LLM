# docker/backend/Dockerfile

# Stage 1: Builder
FROM python:3.11-slim-bookworm AS builder

# Установка build-зависимостей и FFmpeg с необходимыми кодеками
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

# Установка рабочего каталога
WORKDIR /app

# Установка Poetry
RUN pip install poetry==1.7.1

# Копирование файлов зависимостей
COPY backend/pyproject.toml backend/poetry.lock ./

# Установка зависимостей
RUN poetry config virtualenvs.create false \
   && poetry install --no-interaction --no-ansi --only main

# Stage 2: Production
FROM python:3.11-slim-bookworm

# Установка runtime-зависимостей и FFmpeg с необходимыми кодеками
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

# Установка рабочего каталога
WORKDIR /app

# Копирование зависимостей из builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Копирование кода приложения
COPY backend/ .

# Копирование конфигурационных файлов
COPY backend/app/config ./config

# Установка переменной окружения для кэша Hugging Face
ENV HF_HOME=/app/.cache/huggingface

# Создание каталога для кэша
RUN mkdir -p /app/.cache/huggingface

# Создание непривилегированного пользователя
RUN adduser --disabled-password --no-create-home appuser

# Изменение прав собственности на рабочий каталог
RUN chown -R appuser:appuser /app

# Переключение на непривилегированного пользователя
USER appuser

# Создание каталога для логов
RUN mkdir -p /app/logs

# Открытие порта
EXPOSE 8000

# Установка переменных окружения
ENV PYTHONUNBUFFERED=1

# Запуск приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
