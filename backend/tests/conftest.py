# KONSPECTO/backend/tests/conftest.py

import logging
import os
import sys

from pathlib import Path
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio

from httpx import AsyncClient

# Указываем плагины pytest
pytest_plugins = ["pytest_asyncio"]

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Конфигурация логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("tests.conftest")


@pytest.fixture(scope="session")
def app():
    """
    Фикстура для предоставления FastAPI приложения.
    """
    from app.main import app

    return app


@pytest.fixture(scope="session")
def check_redis_url():
    redis_url = os.getenv("REDIS_URL")
    if redis_url is None:
        pytest.skip(
            "REDIS_URL environment variable is not set, skipping tests.",
            allow_module_level=True,
        )


@pytest.fixture(scope="module")
def test_client(app):
    """
    Фикстура предоставляет TestClient для FastAPI приложения.
    """
    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        yield client


@pytest_asyncio.fixture
async def async_client(app):
    """
    Асинхронная фикстура предоставляет AsyncClient для FastAPI приложения.
    Область действия изменена на function (по умолчанию).
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def mock_transcription_model_fixture(app):
    """
    Фикстура для мокинга и установки transcription_model в app.state.
    """
    from unittest.mock import AsyncMock

    from app.services.transcription.base import AbstractTranscriptionModel

    mock_transcription_model = AsyncMock(spec=AbstractTranscriptionModel)
    mock_transcription_model.transcribe.return_value = "Это тестовая транскрипция."

    # Патчим app.state.transcription_model перед запуском тестов
    app.state.transcription_model = mock_transcription_model
    yield mock_transcription_model
    # Очистка после теста
    del app.state.transcription_model
