# tests/conftest.py

import pytest
import os
import logging
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("tests.conftest")

@pytest.fixture(scope="session", autouse=True)
def check_redis_url():
    redis_url = os.getenv("REDIS_URL")
    if redis_url is None:
        pytest.skip("REDIS_URL environment variable is not set, skipping tests.", allow_module_level=True)

@pytest.fixture(scope="module")
def test_client():
    """
    Фикстура для предоставления TestClient для FastAPI приложения.
    """
    # Импортируем приложение после установки PYTHONPATH
    from app.main import app
    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        yield client