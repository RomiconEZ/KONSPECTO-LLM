# KONSPECTO/backend/tests/test_agent_search.py

import pytest
from unittest.mock import patch, MagicMock
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

@patch("app.services.index_service.get_query_engine")
def test_search_success(mock_get_query_engine, mock_query_engine_response):
    # Настраиваем mock для query_engine
    mock_query_engine_instance = MagicMock()
    mock_query_engine_instance.query.return_value = mock_query_engine_response(
        ["Текст первого документа.", "Текст второго документа."]
    )
    mock_get_query_engine.return_value = mock_query_engine_instance

    query = "тестовый запрос"
    results = SearchTool.search(query)

    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0] == "Текст первого документа."
    assert results[1] == "Текст второго документа."

@patch("app.services.index_service.get_query_engine")
def test_search_no_results(mock_get_query_engine):
    # Настраиваем mock для query_engine с пустыми результатами
    mock_query_engine_instance = MagicMock()
    mock_query_engine_instance.query.return_value = mock_query_engine_response = type(
        'MockResponse',
        (object,),
        {'source_nodes': []}
    )()
    mock_get_query_engine.return_value = mock_query_engine_instance

    query = "запрос без результатов"
    results = SearchTool.search(query)

    assert isinstance(results, list)
    assert len(results) == 0

@patch("app.services.index_service.get_query_engine")
def test_search_exception(mock_get_query_engine):
    # Настраиваем mock для query_engine чтобы выбросить исключение
    mock_query_engine_instance = MagicMock()
    mock_query_engine_instance.query.side_effect = Exception("Test Exception")
    mock_get_query_engine.return_value = mock_query_engine_instance

    query = "запрос с ошибкой"

    with pytest.raises(Exception) as exc_info:
        SearchTool.search(query)

    assert "Test Exception" in str(exc_info.value)