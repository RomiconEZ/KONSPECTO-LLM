# KONSPECTO/backend/tests/test_main.py

def test_root(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to KONSPECTO API"}

def test_health_check(test_client):
    response = test_client.get("/health")
    assert response.status_code in [200, 500]

    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "unhealthy"]
    assert "version" in data
    assert "redis_connected" in data
    if data["status"] == "unhealthy":
        assert "error" in data