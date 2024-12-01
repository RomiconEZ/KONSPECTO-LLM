# KONSPECTO/backend/tests/test_transcription.py

import pytest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException
from app.services.transcription.base import AbstractTranscriptionModel
from app.services.transcription.whisper_model import WhisperTranscriptionModel
from app.api.v1.endpoints.transcribe import TranscriptionService

@pytest.fixture
def mock_transcription_model():
    """
    Фикстура для создания мокнутого экземпляра AbstractTranscriptionModel.
    """
    model = AsyncMock(spec=AbstractTranscriptionModel)
    return model

@pytest.mark.asyncio
async def test_transcribe_audio_success(mock_transcription_model):
    """
    Тест успешной транскрипции аудио файла.
    """
    mock_transcription_model.transcribe.return_value = "Это результат транскрипции."

    service = TranscriptionService(transcription_model=mock_transcription_model)
    with patch('aiofiles.open', new_callable=AsyncMock):
        with patch('builtins.open', new_callable=AsyncMock):
            with patch('os.path.getsize', return_value=1024):
                with patch('os.remove') as mock_remove:
                    transcription = await service.transcribe_audio("path/to/audio.mp3")
                    assert transcription == "Это результат транскрипции."
                    mock_transcription_model.transcribe.assert_awaited_once_with("path/to/audio.mp3")

@pytest.mark.asyncio
async def test_transcribe_audio_failure(mock_transcription_model):
    """
    Тест обработки исключения при транскрипции.
    """
    mock_transcription_model.transcribe.side_effect = Exception("Тестовое исключение.")

    service = TranscriptionService(transcription_model=mock_transcription_model)
    with pytest.raises(Exception) as exc_info:
        await service.transcribe_audio("path/to/audio.mp3")
    assert "Тестовое исключение." in str(exc_info.value)