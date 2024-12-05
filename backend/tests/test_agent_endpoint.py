# KONSPECTO/backend/tests/test_agent_endpoint.py

from unittest.mock import ANY, AsyncMock, patch

import pytest

from httpx import AsyncClient

from app.main import app


@pytest.fixture
def mock_search_tool():
    with patch("agent.tools.search.SearchTool.search") as mock_search:
        mock_search.return_value = ["Test search result"]
        yield mock_search


@pytest.fixture
def mock_youtube_to_docx():
    with patch("agent.tools.video_processor.youtube_to_docx") as mock_convert:
        mock_convert.return_value = "docx:12345-abcde"
        yield mock_convert


@pytest.fixture
def mock_agent_executor():
    with patch("agent.react_agent.AgentExecutor.ainvoke") as mock_executor:
        yield mock_executor


@pytest.mark.asyncio
async def test_agent_explain_terminology(mock_agent_executor, async_client):
    mock_agent_executor.return_value = (
        "Определение - Свёрточная нейронная сеть (CNN) — это вид глубокой нейронной сети."
    )

    query = {"query": "Объясни, что такое свёрточная нейронная сеть"}
    response = await async_client.post("/api/v1/agent/", json=query)

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "Определение -" in data["response"]


@pytest.mark.asyncio
async def test_agent_generate_document_with_images(mock_agent_executor, async_client):
    mock_agent_executor.return_value = "Ваш документ был успешно сгенерирован. Вы можете скачать его, используя ключ docx:12345-abcde"

    query = {
        "query": "Сгенерируй документ с изображениями из видео: https://www.youtube.com/watch?v=example"
    }
    response = await async_client.post("/api/v1/agent/", json=query)

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "docx:" in data["response"]


@pytest.mark.asyncio
async def test_agent_unknown_request(mock_agent_executor, async_client):
    mock_agent_executor.return_value = "Извините, я не могу помочь с этим запросом."

    query = {"query": "Неизвестный запрос без инструментов"}
    response = await async_client.post("/api/v1/agent/", json=query)

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "Извините, я не могу помочь с этим запросом." in data["response"]
