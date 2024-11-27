# KONSPECTO/backend/tests/test_video_processor.py

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from fastapi import HTTPException

from app.agent.tools.video_processor import youtube_to_docx, are_images_different_ssim


@pytest.fixture
def mock_pytubefix():
    with patch("app.agent.tools.video_processor.YouTube") as mock:
        yield mock


@pytest.fixture
def mock_cv2():
    with patch("app.agent.tools.video_processor.cv2.VideoCapture") as mock:
        yield mock


@pytest.fixture
def mock_ssim():
    with patch("app.agent.tools.video_processor.ssim") as mock:
        yield mock


@pytest.fixture
def mock_pil_image():
    with patch("app.agent.tools.video_processor.Image") as mock:
        yield mock


@pytest.fixture
def mock_docx():
    with patch("app.agent.tools.video_processor.Document") as mock:
        yield mock


@pytest.fixture
def mock_on_progress():
    with patch("app.agent.tools.video_processor.on_progress") as mock:
        yield mock


def test_are_images_different_ssim_true(mock_ssim):
    # Настройка mock для SSIM, чтобы вернуть значение ниже порога
    mock_ssim.return_value = (0.95, None)  # less than 0.98
    result = are_images_different_ssim("img1.png", "img2.png", threshold=0.98)
    assert result is True
    mock_ssim.assert_called_once()


def test_are_images_different_ssim_false(mock_ssim):
    # Настройка mock для SSIM, чтобы вернуть значение выше порога
    mock_ssim.return_value = (0.99, None)  # greater than or equal to 0.98
    result = are_images_different_ssim("img1.png", "img2.png", threshold=0.98)
    assert result is False
    mock_ssim.assert_called_once()


def test_are_images_different_ssim_exception(mock_ssim):
    # Настройка mock для SSIM, чтобы выбросить исключение
    mock_ssim.side_effect = Exception("SSIM Error")
    result = are_images_different_ssim("img1.png", "img2.png", threshold=0.98)
    assert result is True  # В случае ошибки считаем изображения различными


@patch("app.agent.tools.video_processor.are_images_different_ssim")
def test_youtube_to_docx_success(mock_compare, mock_pytubefix, mock_cv2, mock_pil_image, mock_docx, mock_on_progress):
    # Настройка фикстур
    mock_compare.return_value = False  # Все изображения схожи, кроме первого

    mock_stream = MagicMock()
    mock_stream.download.return_value = None

    mock_yt = MagicMock()
    mock_yt.title = "Test Video"
    mock_pytubefix.return_value = mock_yt
    mock_yt.streams.get_highest_resolution.return_value = mock_stream

    cap_mock = MagicMock()
    cap_mock.get.return_value = 30  # FPS
    # Симуляция чтения кадров: сначала True, потом False
    cap_mock.read.side_effect = [
        (True, "frame1"),
        (True, "frame2"),
        (False, None)
    ]
    mock_cv2.return_value = cap_mock

    mock_doc = MagicMock()
    mock_docx.return_value = mock_doc

    youtube_url = "https://www.youtube.com/watch?v=example"
    docx_path = youtube_to_docx(youtube_url)

    assert "generated_docs" in docx_path
    mock_pytubefix.assert_called_once_with(youtube_url, on_progress_callback=mock_on_progress)
    mock_yt.streams.get_highest_resolution.assert_called_once()
    mock_stream.download.assert_called_once_with(output_path=tempfile.gettempdir(), filename="video.mp4")
    mock_cv2.assert_called_once_with(os.path.join(tempfile.gettempdir(), "video.mp4"))
    mock_doc.save.assert_called_once()
    mock_compare.assert_called()  # Проверяем, что функция сравнения вызывалась


@patch("app.agent.tools.video_processor.YouTube")
def test_youtube_to_docx_invalid_url(mock_yt, mock_cv2, mock_pil_image, mock_docx, mock_on_progress):
    # Настройка mock для YouTube, чтобы выбросить исключение при неверном URL
    mock_yt.side_effect = Exception("Invalid URL Format")
    youtube_url = "invalid_url"
    with pytest.raises(HTTPException) as exc_info:
        youtube_to_docx(youtube_url)
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Не удалось обработать видео."


@patch("app.agent.tools.video_processor.YouTube")
def test_youtube_to_docx_no_stream(mock_yt, mock_cv2, mock_pil_image, mock_docx, mock_on_progress):
    # Настройка mock для YouTube без доступных потоков
    mock_yt_instance = MagicMock()
    mock_yt_instance.streams.get_highest_resolution.return_value = None
    mock_yt.return_value = mock_yt_instance

    youtube_url = "https://www.youtube.com/watch?v=example"
    with pytest.raises(ValueError) as exc_info:
        youtube_to_docx(youtube_url)
    assert str(exc_info.value) == "Не удалось найти подходящий поток для загрузки."