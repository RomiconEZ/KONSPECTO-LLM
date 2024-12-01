# KONSPECTO/backend/tests/test_search.py

import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_search(async_client):
    with patch('app.api.v1.endpoints.search.SearchService.process_search') as mock_process_search:
        mock_process_search.return_value = []

        response = await async_client.post("/api/v1/search/", json={"query": "тестовый запрос"})
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)


@pytest.mark.asyncio
async def test_search_invalid_payload(async_client):
    response = await async_client.post("/api/v1/search/", json={"invalid_key": "тест"})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data