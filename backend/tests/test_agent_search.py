# KONSPECTO/backend/tests/test_agent_search.py

from unittest.mock import MagicMock, patch

import pytest

from agent.tools.search import SearchTool


@pytest.fixture
def mock_query_engine_response():
    class MockNode:
        def __init__(self, text):
            self.text = text

    class MockNodeWithScore:
        def __init__(self, node):
            self.node = node

    class MockResponse:
        def __init__(self, texts):
            self.source_nodes = [MockNodeWithScore(MockNode(text)) for text in texts]

    return MockResponse


@patch("agent.tools.search.get_query_engine")  # Обновленный путь патча
def test_search_success(mock_get_query_engine, mock_query_engine_response):
    # Настройка мокового query engine
    mock_query_engine_instance = MagicMock()
    mock_query_engine_instance.query.return_value = mock_query_engine_response(
        ["Text of the first document.", "Text of the second document."]
    )
    mock_get_query_engine.return_value = mock_query_engine_instance

    query = "test query"
    results = SearchTool.search(query)

    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0] == "Text of the first document."
    assert results[1] == "Text of the second document."


@patch("agent.tools.search.get_query_engine")  # Обновленный путь патча
def test_search_exception(mock_get_query_engine):
    # Настройка мокового query engine для генерации исключения
    mock_query_engine_instance = MagicMock()
    mock_query_engine_instance.query.side_effect = Exception("Test Exception")
    mock_get_query_engine.return_value = mock_query_engine_instance

    query = "query causing error"

    with pytest.raises(Exception) as exc_info:
        SearchTool.search(query)

    assert "Test Exception" in str(exc_info.value)
