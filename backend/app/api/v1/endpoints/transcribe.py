# backend/app/api/v1/endpoints/transcribe.py

from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
import aiofiles
import tempfile
import os
import logging
from faster_whisper import WhisperModel

router = APIRouter()
logger = logging.getLogger("app.api.v1.endpoints.transcribe")


def get_whisper_model(request: Request) -> WhisperModel:
    """
    Зависимость для получения экземпляра WhisperModel из состояния приложения.

    :param request: Объект Request FastAPI.
    :return: Экземпляр WhisperModel.
    """
    return request.app.state.whisper_model


class TranscriptionService:
    """
    Сервисный класс для обработки транскрипции аудио файлов.
    """

    def __init__(self, model: WhisperModel):
        """
        Инициализация TranscriptionService с заданной моделью WhisperModel.

        :param model: Экземпляр WhisperModel для транскрипции.
        """
        self.model = model
        self.temp_file = None

    async def validate_and_save_file(self, file: UploadFile) -> str:
        """
        Валидирует и сохраняет загруженный файл во временное хранилище.

        :param file: Загруженный аудио файл.
        :return: Путь к сохраненному файлу.
        """
        # Проверка типа контента
        if not file.content_type.startswith("audio/"):
            logger.warning(f"Invalid content type: {file.content_type}")
            raise HTTPException(status_code=400, detail="Invalid file type. Audio file required.")

        # Проверка расширения файла
        _, file_ext = os.path.splitext(file.filename)
        if file_ext.lower() not in ['.mp3', '.wav']:
            logger.warning(f"Unsupported file extension: {file_ext}")
            raise HTTPException(status_code=400, detail="Unsupported file format. Use MP3 or WAV.")

        # Сохранение файла во временное хранилище
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            self.temp_file = tmp.name
            async with aiofiles.open(self.temp_file, 'wb') as out_file:
                content = await file.read()  # Асинхронное чтение
                await out_file.write(content)

        # Проверка, что файл не пустой
        if os.path.getsize(self.temp_file) == 0:
            logger.error("Uploaded file is empty.")
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        # Логирование размера файла
        file_size = os.path.getsize(self.temp_file)
        logger.debug(f"Uploaded file size: {file_size} bytes")

        return self.temp_file

    def transcribe_audio(self, file_path: str) -> str:
        """
        Выполняет транскрипцию аудио файла с помощью WhisperModel.

        :param file_path: Путь к аудио файлу.
        :return: Текст транскрипции.
        """
        logger.debug(f"Starting transcription for file: {file_path}")
        segments, _ = self.model.transcribe(
            file_path,
            task="transcribe",
            without_timestamps=True,
            beam_size=1,
            language="ru",
            condition_on_previous_text=False
        )

        # Объединение сегментов текста
        transcription = " ".join([segment.text for segment in segments])
        logger.info(f"Transcription completed successfully for file: {file_path}")
        return transcription

    def cleanup(self):
        """
        Очищает временные файлы, созданные в процессе обработки.
        """
        if self.temp_file and os.path.exists(self.temp_file):
            os.remove(self.temp_file)
            logger.debug(f"Removed temporary file: {self.temp_file}")


@router.post("/")
async def transcribe_audio(
    file: UploadFile = File(...),
    model: WhisperModel = Depends(get_whisper_model)
):
    """
    Эндпойнт для транскрипции загруженного аудио файла с использованием WhisperModel.
    Поддерживает форматы MP3 и WAV.

    :param file: Загруженный аудио файл.
    :param model: Экземпляр WhisperModel.
    :return: JSON ответ с текстом транскрипции.
    """
    service = TranscriptionService(model)
    try:
        file_path = await service.validate_and_save_file(file)
        transcription = service.transcribe_audio(file_path)
        return JSONResponse(content={"transcription": transcription})
    except HTTPException as he:
        raise he  # Передача HTTPException без изменений
    except Exception:
        logger.exception("Failed to transcribe audio.")
        raise HTTPException(status_code=500, detail="Failed to transcribe audio.")
    finally:
        service.cleanup()