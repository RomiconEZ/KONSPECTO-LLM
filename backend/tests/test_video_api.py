# KONSPECTO/backend/tests/test_video_api.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app

client = TestClient(app)


@patch("app.api.v1.endpoints.video.youtube_to_docx")
@patch("app.api.v1.endpoints.video.RedisService")
def test_convert_youtube_to_docx_success(mock_redis_service, mock_youtube_to_docx):
    mock_youtube_to_docx.return_value = "docx:123e4567-e89b-12d3-a456-426614174000"

    response = client.post(
        "/api/v1/youtube_to_docx",
        json={"youtube_url": "https://www.youtube.com/watch?v=example"}
    )

    assert response.status_code == 200
    assert response.json() == {"docx_key": "docx:123e4567-e89b-12d3-a456-426614174000"}


@patch("app.api.v1.endpoints.video.RedisService")
def test_get_docx_file_success(mock_redis_service):
    mock_redis_service.return_value.get_file.return_value = b"Fake DOCX content"

    response = client.get("/api/v1/video/docx:123e4567-e89b-12d3-a456-426614174000")

    assert response.status_code == 200
    assert response.headers[
               "Content-Disposition"] == 'attachment; filename="docx:123e4567-e89b-12d3-a456-426614174000.docx"'
    assert response.content == b"Fake DOCX content"


@patch("app.api.v1.endpoints.video.RedisService")
def test_get_docx_file_not_found(mock_redis_service):
    mock_redis_service.return_value.get_file.return_value = None

    response = client.get("/api/v1/video/docx:nonexistentkey")

    assert response.status_code == 404
    assert response.json() == {"detail": "Документ не найден."}