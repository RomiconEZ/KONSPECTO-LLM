# KONSPECTO/backend/tests/test_transcribe_endpoint.py

from unittest.mock import AsyncMock, patch

import pytest

from fastapi import HTTPException

from app.services.transcription.base import AbstractTranscriptionModel
from app.services.transcription.whisper_model import WhisperTranscriptionModel


@pytest.mark.asyncio
async def test_transcribe_audio_success(async_client, mock_transcription_model_fixture):
    """
    Тест успешной транскрипции аудио файла.
    """
    response = await async_client.post(
        "/api/v1/transcribe/",
        files={"file": ("test.mp3", b"Fake audio content", "audio/mpeg")},
    )

    assert response.status_code == 200
    assert response.json() == {"transcription": "Это тестовая транскрипция."}


@pytest.mark.asyncio
async def test_transcribe_audio_invalid_file_type(
    async_client, mock_transcription_model_fixture
):
    """
    Тест отправки файла с неверным типом контента.
    """
    response = await async_client.post(
        "/api/v1/transcribe/",
        files={"file": ("test.txt", b"Fake text content", "text/plain")},
    )

    assert response.status_code == 400
    assert "Недопустимый тип файла" in response.json()["detail"]


@pytest.mark.asyncio
async def test_transcribe_audio_unsupported_extension(
    async_client, mock_transcription_model_fixture
):
    """
    Тест отправки файла с неподдерживаемым расширением.
    """
    response = await async_client.post(
        "/api/v1/transcribe/",
        files={"file": ("test.exe", b"Fake executable content", "audio/mpeg")},
    )

    assert response.status_code == 400
    assert "Неподдерживаемый формат файла" in response.json()["detail"]
