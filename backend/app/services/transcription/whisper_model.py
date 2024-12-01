# KONSPECTO/backend/app/services/transcription/whisper_model.py

import logging
from .base import AbstractTranscriptionModel
from faster_whisper import WhisperModel
import torch

logger = logging.getLogger("app.services.transcription.whisper_model")


class WhisperTranscriptionModel(AbstractTranscriptionModel):
    def __init__(self, model_size: str = "large-v3"):
        """
        Инициализация WhisperTranscriptionModel.

        :param model_size: Размер модели Whisper для использования.
        """
        self.model_size = model_size
        self.model = None  # Будет загружена при вызове load_model

    def load_model(self):
        """
        Загружает модель Whisper.
        """
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float32"  # Можно изменить в зависимости от требований
        cpu_threads = 8

        try:
            self.model = WhisperModel(
                self.model_size,
                device=device,
                compute_type=compute_type,
                cpu_threads=cpu_threads
            )
            logger.info(f"Whisper модель '{self.model_size}' успешно загружена на устройстве {device}.")
        except Exception as e:
            logger.exception(f"Не удалось загрузить модель Whisper: {e}")
            raise

    async def transcribe(self, file_path: str) -> str:
        """
        Выполняет транскрипцию аудио файла с помощью WhisperModel.

        :param file_path: Путь к аудио файлу.
        :return: Текст транскрипции.
        """
        if self.model is None:
            self.load_model()

        logger.debug(f"Начало транскрипции файла: {file_path}")
        try:
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
            logger.info(f"Транскрипция успешно завершена для файла: {file_path}")
            return transcription
        except Exception as e:
            logger.exception(f"Транскрипция не выполнена для файла {file_path}: {e}")
            raise