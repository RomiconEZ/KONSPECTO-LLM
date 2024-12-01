# KONSPECTO/backend/tests/test_transcribe_endpoint.py

import pytest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import app
from app.models.transcription import TranscriptionResponse

client = TestClient(app)

@pytest.fixture
def mock_transcription_model():
    """
    Фикстура для мока модели транскрибации.
    """
    with patch('app.api.v1.endpoints.transcribe.AbstractTranscriptionModel') as mock_model:
        instance = mock_model.return_value
        instance.transcribe = AsyncMock(return_value="Это тестовая транскрипция.")
        yield instance

def test_transcribe_audio_success(mock_transcription_model):
    """
    Тест успешной транскрипции через эндпойнт.
    """
    with patch('app.api.v1.endpoints.transcribe.TranscriptionService.transcribe_audio', new_callable=AsyncMock) as mock_transcribe_audio:
        mock_transcribe_audio.return_value = "Это тестовая транскрипция."

        response = client.post(
            "/api/v1/transcribe/",
            files={"file": ("test.mp3", b"Fake audio content", "audio/mpeg")}
        )

        assert response.status_code == 200
        assert response.json() == {"transcription": "Это тестовая транскрипция."}
        mock_transcribe_audio.assert_awaited_once()

def test_transcribe_audio_invalid_file_type():
    """
    Тест отправки недопустимого типа файла.
    """
    response = client.post(
        "/api/v1/transcribe/",
        files={"file": ("test.txt", b"Fake text content", "text/plain")}
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Недопустимый тип файла. Требуется аудио файл."}

def test_transcribe_audio_unsupported_extension():
    """
    Тест отправки файла с неподдерживаемым расширением.
    """
    response = client.post(
        "/api/v1/transcribe/",
        files={"file": ("test.exe", b"Fake executable content", "application/octet-stream")}
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Неподдерживаемый формат файла. Используйте MP3 или WAV."}