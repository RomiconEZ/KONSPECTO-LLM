# KONSPECTO/backend/tests/test_main.py

import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_root(async_client):
    response = await async_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Добро пожаловать в KONSPECTO API"}


@pytest.mark.asyncio
async def test_health_check(async_client):
    response = await async_client.get("/health")
    # The expected possible status codes are 200 or 500
    assert response.status_code in [200, 500]

    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "unhealthy"]
    assert "version" in data
    assert "redis_connected" in data
    if data["status"] == "unhealthy":
        pass  # Further checks can be added if needed