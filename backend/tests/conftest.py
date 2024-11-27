# tests/conftest.py

import pytest
from testcontainers.redis import RedisContainer
import os
from fastapi.testclient import TestClient
from app.main import app
import time
import logging
from docker.errors import DockerException
import docker

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("tests.conftest")

@pytest.fixture(scope="session", autouse=True)
def check_docker():
    try:
        client = docker.from_env()
        client.ping()
        logger.info("Docker доступен и отвечает на запросы.")
    except DockerException as e:
        logger.error("Docker недоступен или не отвечает.")
        logger.error(f"DockerException: {e}")
        pytest.skip("Docker не доступен, пропуск тестов.", allow_module_level=True)
    except FileNotFoundError as e:
        logger.error("Docker не установлен или сокет Docker недоступен.")
        logger.error(f"FileNotFoundError: {e}")
        pytest.skip("Docker не установлен или сокет Docker недоступен, пропуск тестов.", allow_module_level=True)

@pytest.fixture(scope="session", autouse=True)
def redis_container():
    try:
        logger.info("Попытка запуска контейнера Redis с помощью testcontainers...")
        with RedisContainer() as redis:
            redis_host = redis.get_container_host_ip()
            redis_port = redis.get_exposed_port(6379)
            redis_url = f"redis://{redis_host}:{redis_port}"
            os.environ["REDIS_URL"] = redis_url
            logger.info(f"Redis контейнер запущен на {redis_url}")
            # Подождать несколько секунд, чтобы убедиться, что Redis полностью запущен
            time.sleep(2)
            yield
    except DockerException as e:
        logger.error("Не удалось запустить Redis контейнер. Убедитесь, что Docker запущен и доступен.")
        logger.error(f"DockerException: {e}")
        pytest.skip("Docker не доступен, пропуск тестов.", allow_module_level=True)
    except FileNotFoundError as e:
        logger.error("Docker сокет не найден.")
        logger.error(f"FileNotFoundError: {e}")
        pytest.skip("Docker сокет не найден, пропуск тестов.", allow_module_level=True)

@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client
