# backend/Dockerfile

# Используем базовый образ с Debian Bookworm
FROM python:3.11-slim-bookworm

# Установить рабочую директорию
WORKDIR /app

# Установка системных зависимостей
RUN echo "Step 1: Updating package list and installing system dependencies" \
    && apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        ca-certificates \
        libsqlite3-dev \
        sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry
RUN echo "Step 2: Installing poetry" \
    && pip install poetry==1.7.1

# Копирование файлов зависимостей Poetry
COPY backend/pyproject.toml ./
COPY backend/poetry.lock ./

# Конфигурация Poetry и установка зависимостей
RUN echo "Step 3: Configuring poetry and installing dependencies" \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Копирование кода бэкенда
COPY backend/ .

# Создание директории для логов
RUN echo "Step 4: Creating logs directory" \
    && mkdir -p /app/logs

# Экспонирование порта
EXPOSE 8000

# Команда для запуска приложения
CMD echo "Step 5: Starting Uvicorn server" \
    && uvicorn app.main:app --host 0.0.0.0 --port 8000