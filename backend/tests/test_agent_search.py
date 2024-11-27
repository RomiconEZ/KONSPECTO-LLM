# KONSPECTO/backend/tests/test_agent_search.py

import pytest
from unittest.mock import patch

from ..agent.tools.search import search


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


@patch("app.agent.tools.search.query_engine")
def test_search_success(mock_query_engine, mock_query_engine_response):
    # Настраиваем mock для query_engine
    mock_query_engine.query.return_value = mock_query_engine_response(
        ["Текст первого документа.", "Текст второго документа."])

    query = "тестовый запрос"
    results = search(query)

    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0] == "Текст первого документа."
    assert results[1] == "Текст второго документа."


@patch("app.agent.tools.search.query_engine")
def test_search_no_results(mock_query_engine):
    # Настраиваем mock для query_engine с пустыми результатами
    mock_query_engine.query.return_value = mock_query_engine_response([])

    query = "запрос без результатов"
    results = search(query)

    assert isinstance(results, list)
    assert len(results) == 0


@patch("app.agent.tools.search.query_engine")
def test_search_exception(mock_query_engine):
    # Настраиваем mock для query_engine чтобы выбросить исключение
    mock_query_engine.query.side_effect = Exception("Test Exception")

    query = "запрос с ошибкой"

    with pytest.raises(Exception) as exc_info:
        search(query)

    assert "Test Exception" in str(exc_info.value)