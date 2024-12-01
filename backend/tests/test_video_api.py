# tests/test_video_api.py

import pytest  # Add this import statement
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_convert_youtube_to_docx_success(async_client):
    with patch('app.api.v1.endpoints.video.VideoService.convert_youtube_video', new_callable=AsyncMock) as mock_convert:
        mock_convert.return_value = "docx:123e4567-e89b-12d3-a456-426614174000"
        response = await async_client.post(
            "/api/v1/video/youtube_to_docx",
            json={"youtube_url": "https://www.youtube.com/watch?v=example"}
        )

        assert response.status_code == 200
        assert response.json() == {"docx_key": "docx:123e4567-e89b-12d3-a456-426614174000"}

@pytest.mark.asyncio
async def test_get_docx_file_success(async_client):
    file_content = b"Fake DOCX content"
    with patch('app.api.v1.endpoints.video.VideoService.get_docx_file', new_callable=AsyncMock) as mock_get_docx_file:
        mock_get_docx_file.return_value = file_content

        response = await async_client.get("/api/v1/video/video/docx:123e4567-e89b-12d3-a456-426614174000")

        assert response.status_code == 200
        assert response.headers[
            "Content-Disposition"] == 'attachment; filename="docx:123e4567-e89b-12d3-a456-426614174000.docx"'
        assert response.content == file_content

@pytest.mark.asyncio
async def test_get_docx_file_not_found(async_client):
    with patch('app.api.v1.endpoints.video.VideoService.get_docx_file', new_callable=AsyncMock) as mock_get_docx_file:
        mock_get_docx_file.side_effect = HTTPException(status_code=404, detail="Документ не найден.")

        response = await async_client.get("/api/v1/video/video/docx:nonexistentkey")

        assert response.status_code == 404
        assert response.json() == {"detail": "Документ не найден."}