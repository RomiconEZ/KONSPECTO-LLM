# backend/tests/test_search.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_search():
    response = client.post("/v1/search", json={"query": "test query"})
    assert response.status_code == 200
    assert "full_result" in response.json()
    assert "abbreviated_result" in response.json()
    assert "source" in response.json()