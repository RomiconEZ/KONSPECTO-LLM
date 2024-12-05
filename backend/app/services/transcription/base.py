# KONSPECTO/backend/app/services/transcription/base.py

from abc import ABC, abstractmethod


class AbstractTranscriptionModel(ABC):
    @abstractmethod
    async def transcribe(self, file_path: str) -> str:
        """
        Асинхронно выполняет транскрипцию аудио файла.

        :param file_path: Путь к аудио файлу.
        :return: Текст транскрипции.
        """
        pass
