# KONSPECTO/backend/tests/test_video_processor.py

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.agent.tools.video_processor import youtube_to_docx, are_images_different_ssim
from app.main import app
from app.services.redis_service import RedisService

client = TestClient(app)

@pytest.fixture
def mock_redis_service():
    with patch("app.agent.tools.video_processor.RedisService") as mock:
        instance = mock.return_value
        instance.set_file = MagicMock(return_value=True)
        yield instance

@patch("app.agent.tools.video_processor.are_images_different_ssim")
@patch("app.agent.tools.video_processor.YouTube")
@patch("app.agent.tools.video_processor.cv2.VideoCapture")
@patch("app.agent.tools.video_processor.Document")
async def test_youtube_to_docx_success(mock_doc, mock_cv2, mock_youtube, mock_ssim, mock_redis_service):
    # Настройка mock для YouTube
    mock_stream = MagicMock()
    mock_stream.download.return_value = None

    mock_yt = MagicMock()
    mock_yt.title = "Test Video"
    mock_youtube.return_value = mock_yt
    mock_yt.streams.get_highest_resolution.return_value = mock_stream

    # Настройка mock для cv2.VideoCapture
    cap_mock = MagicMock()
    cap_mock.get.return_value = 30  # FPS
    cap_mock.read.side_effect = [
        (True, "frame1"),
        (True, "frame2"),
        (False, None)
    ]
    mock_cv2.return_value = cap_mock

    # Настройка mock для SSIM
    mock_ssim.return_value = (0.95, None)  # Images are different

    # Настройка mock для Document
    mock_doc_instance = MagicMock()
    mock_doc.return_value = mock_doc_instance

    youtube_url = "https://www.youtube.com/watch?v=example"
    redis_service = mock_redis_service

    # Вызов функции
    docx_key = await youtube_to_docx(youtube_url, redis_service)

    # Проверки
    assert docx_key.startswith("docx:")
    mock_youtube.assert_called_once_with(youtube_url, on_progress_callback=mock_progress)
    mock_stream.download.assert_called_once()
    mock_cv2.assert_called_once_with(os.path.join(tempfile.gettempdir(), "video.mp4"))
    mock_doc_instance.save.assert_called_once()
    mock_redis_service.set_file.assert_called_once()
    mock_ssim.assert_called()

async def mock_progress(*args, **kwargs):
    pass