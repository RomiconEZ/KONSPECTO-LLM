# KONSPECTO/backend/tests/test_search.py

from unittest.mock import patch
import pytest

def test_search(test_client):
    with patch('app.api.v1.endpoints.search.SearchService.process_search') as mock_process_search:
        # Мокируем метод process_search для возврата тестовых данных
        mock_process_search.return_value = []

        response = test_client.post("/api/v1/search/", json={"query": "тестовый запрос"})
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)
        # Добавьте дополнительные проверки структуры данных, если необходимо

def test_search_invalid_payload(test_client):
    response = test_client.post("/api/v1/search/", json={"invalid_key": "тест"})
    assert response.status_code == 422  # Unprocessable Entity
    data = response.json()
    assert "detail" in data