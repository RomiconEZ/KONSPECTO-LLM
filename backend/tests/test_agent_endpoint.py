from unittest.mock import AsyncMock

import pytest

from app.api.v1.endpoints.agent import get_agent_service


@pytest.fixture
def mock_agent_service(app):
    mock_service = AsyncMock()
    app.dependency_overrides[get_agent_service] = lambda: mock_service
    yield mock_service
    app.dependency_overrides.pop(get_agent_service, None)


@pytest.mark.asyncio
async def test_agent_explain_terminology(mock_agent_service, async_client):
    mock_agent_service.process_query.return_value = (
        "Определение - Свёрточная нейронная сеть (CNN) — это вид глубокой нейронной сети."
    )

    query = {"query": "Объясни, что такое свёрточная нейронная сеть"}
    response = await async_client.post("/api/v1/agent/", json=query)

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "Определение -" in data["response"]
    mock_agent_service.process_query.assert_awaited_once_with(query["query"])


@pytest.mark.asyncio
async def test_agent_generate_document_with_images(mock_agent_service, async_client):
    mock_agent_service.process_query.return_value = "Ваш документ был успешно сгенерирован. Вы можете скачать его, используя ключ docx:12345-abcde"

    query = {
        "query": "Сгенерируй документ с изображениями из видео: https://www.youtube.com/watch?v=example"
    }
    response = await async_client.post("/api/v1/agent/", json=query)

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "docx:" in data["response"]
    mock_agent_service.process_query.assert_awaited_once_with(query["query"])


@pytest.mark.asyncio
async def test_agent_unknown_request(mock_agent_service, async_client):
    mock_agent_service.process_query.return_value = (
        "Извините, я не могу помочь с этим запросом."
    )

    query = {"query": "Неизвестный запрос без инструментов"}
    response = await async_client.post("/api/v1/agent/", json=query)

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "Извините, я не могу помочь с этим запросом." in data["response"]
    mock_agent_service.process_query.assert_awaited_once_with(query["query"])
