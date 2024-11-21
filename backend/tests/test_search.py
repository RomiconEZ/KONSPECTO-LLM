# backend/tests/test_search.py
from fastapi.testclient import TestClient
import pytest

from app.main import app

client = TestClient(app)

def test_search():
    response = client.post("/api/v1/search", json={"query": "test query"})
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)
    # Further assertions can be added based on expected structure

def test_search_invalid_payload():
    response = client.post("/api/v1/search", json={"invalid_key": "test"})
    assert response.status_code == 422  # Unprocessable Entity
    data = response.json()
    assert "detail" in data