# backend/tests/test_main.py
from fastapi.testclient import TestClient
import pytest

from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to KONSPECTO API"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code in [200, 500]

    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "unhealthy"]
    assert "version" in data
    assert "redis_connected" in data
    if data["status"] == "unhealthy":
        assert "error" in data