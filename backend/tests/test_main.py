from fastapi.testclient import TestClient

from app.main import app
client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code in [200, 500]

    if response.status_code == 200:
        assert response.json()["status"] in ["healthy", "unhealthy"]
    elif response.status_code == 500:
        assert response.json()["status"] == "unhealthy"
    else:
        raise AssertionError(f"Unexpected status code: {response.status_code}")