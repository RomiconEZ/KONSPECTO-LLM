# KONSPECTO/backend/app/api/v1/endpoints/transcribe.py

import logging
import os
import tempfile

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile

from ....models.transcription import TranscriptionResponse
from ....services.transcription.base import AbstractTranscriptionModel

router = APIRouter()
logger = logging.getLogger("app.api.v1.endpoints.transcribe")


class TranscriptionService:
    """
    Сервисный класс для обработки транскрипции аудио файлов.
    """

    def __init__(self, transcription_model: AbstractTranscriptionModel):
        """
        Инициализация TranscriptionService с заданной моделью транскрибации.

        :param transcription_model: Экземпляр AbstractTranscriptionModel.
        """
        self.transcription_model = transcription_model
        self.temp_file = None

    async def validate_and_save_file(self, file: UploadFile) -> str:
        """
        Валидирует и сохраняет загруженный файл во временное хранилище.

        :param file: Загруженный аудио файл.
        :return: Путь к сохраненному файлу.
        :raises HTTPException: Если файл невалиден или не может быть сохранен.
        """
        if not file.content_type.startswith("audio/"):
            logger.warning(f"Invalid content type: {file.content_type}")
            raise HTTPException(
                status_code=400, detail="Недопустимый тип файла. Требуется аудио файл."
            )

        _, file_ext = os.path.splitext(file.filename)
        if file_ext.lower() not in [".mp3", ".wav"]:
            logger.warning(f"Unsupported file extension: {file_ext}")
            raise HTTPException(
                status_code=400,
                detail="Неподдерживаемый формат файла. Используйте MP3 или WAV.",
            )

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            self.temp_file = tmp.name
            async with aiofiles.open(self.temp_file, "wb") as out_file:
                content = await file.read()
                await out_file.write(content)

        if os.path.getsize(self.temp_file) == 0:
            logger.error("Uploaded file is empty.")
            raise HTTPException(status_code=400, detail="Загруженный файл пустой.")

        file_size = os.path.getsize(self.temp_file)
        logger.debug(f"Uploaded file size: {file_size} bytes")

        return self.temp_file

    async def transcribe_audio(self, file_path: str) -> str:
        """
        Выполняет транскрипцию аудио файла с помощью модели транскрибации.

        :param file_path: Путь к аудио файлу.
        :return: Текст транскрипции.
        """
        transcription = await self.transcription_model.transcribe(file_path)
        return transcription

    def cleanup(self):
        """
        Очищает временные файлы.
        """
        if self.temp_file and os.path.exists(self.temp_file):
            os.remove(self.temp_file)
            logger.debug(f"Removed temporary file: {self.temp_file}")


def get_transcription_model(request: Request) -> AbstractTranscriptionModel:
    """
    Зависимость для получения экземпляра AbstractTranscriptionModel из состояния приложения.

    :param request: Объект запроса FastAPI.
    :return: Экземпляр AbstractTranscriptionModel.
    """
    return request.app.state.transcription_model


@router.post("/", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    transcription_model: AbstractTranscriptionModel = Depends(get_transcription_model),
):
    """
    Эндпойнт для транскрипции загруженного аудио файла.

    :param file: Загруженный аудио файл.
    :param transcription_model: Экземпляр модели транскрибации.
    :return: JSON ответ с текстом транскрипции.
    """
    service = TranscriptionService(transcription_model)
    try:
        file_path = await service.validate_and_save_file(file)
        transcription = await service.transcribe_audio(file_path)
        return TranscriptionResponse(transcription=transcription)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to transcribe audio.")
        raise HTTPException(
            status_code=500, detail="Не удалось выполнить транскрипцию аудио."
        )
    finally:
        service.cleanup()
