# KONSPECTO/backend/tests/test_video_processor.py

from unittest.mock import patch, MagicMock
import pytest
from agent.tools.video_processor import youtube_to_docx, VideoProcessingError, InvalidYouTubeURLException
from fastapi import HTTPException

@pytest.mark.asyncio
@patch("agent.tools.video_processor.VideoToDocxConverter")
async def test_youtube_to_docx_success(mock_converter_class):
    # Мокируем методы экземпляра
    mock_converter = MagicMock()
    mock_converter.process.return_value = "docx:unique_key"
    mock_converter_class.return_value = mock_converter

    youtube_url = "https://www.youtube.com/watch?v=example"
    redis_service = MagicMock()

    # Вызов функции
    docx_key = await youtube_to_docx(youtube_url, redis_service)

    # Проверки
    assert docx_key == "docx:unique_key"
    mock_converter_class.assert_called_once_with(youtube_url, redis_service, difference_checker=None, expire_seconds=86400)
    mock_converter.process.assert_called_once()

@pytest.mark.asyncio
@patch("agent.tools.video_processor.VideoToDocxConverter")
async def test_youtube_to_docx_invalid_url(mock_converter_class):
    # Мокируем экземпляр для возбуждения InvalidYouTubeURLException
    mock_converter = MagicMock()
    mock_converter.process.side_effect = InvalidYouTubeURLException()
    mock_converter_class.return_value = mock_converter

    youtube_url = "invalid_url"
    redis_service = MagicMock()

    with pytest.raises(InvalidYouTubeURLException):
        await youtube_to_docx(youtube_url, redis_service)

    mock_converter_class.assert_called_once()
    mock_converter.process.assert_called_once()

@pytest.mark.asyncio
@patch("agent.tools.video_processor.VideoToDocxConverter")
async def test_youtube_to_docx_processing_error(mock_converter_class):
    # Мокируем экземпляр для возбуждения VideoProcessingError
    mock_converter = MagicMock()
    mock_converter.process.side_effect = VideoProcessingError()
    mock_converter_class.return_value = mock_converter

    youtube_url = "https://www.youtube.com/watch?v=example"
    redis_service = MagicMock()

    with pytest.raises(VideoProcessingError):
        await youtube_to_docx(youtube_url, redis_service)

    mock_converter_class.assert_called_once()
    mock_converter.process.assert_called_once()