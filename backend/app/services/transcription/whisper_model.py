# KONSPECTO/backend/app/services/transcription/whisper_model.py

import logging

import torch

from faster_whisper import WhisperModel

from .base import AbstractTranscriptionModel

logger = logging.getLogger("app.services.transcription.whisper_model")


class WhisperTranscriptionModel(AbstractTranscriptionModel):
    def __init__(self, model_size: str = "large-v3"):
        """
        Initialize the WhisperTranscriptionModel.

        :param model_size: The size of the Whisper model to use.
        """
        self.model_size = model_size
        self.model = None  # Will be loaded upon calling load_model

    def load_model(self):
        """
        Load the Whisper model.
        """
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float32"  # Can be changed depending on requirements
        cpu_threads = 8

        try:
            self.model = WhisperModel(
                self.model_size,
                device=device,
                compute_type=compute_type,
                cpu_threads=cpu_threads,
            )
            logger.info(
                f"Whisper model '{self.model_size}' loaded successfully on device {device}."
            )
        except Exception as e:
            logger.exception(f"Failed to load Whisper model: {e}")
            raise

    async def transcribe(self, file_path: str) -> str:
        """
        Perform transcription of an audio file using WhisperModel.

        :param file_path: Path to the audio file.
        :return: Transcription text.
        """
        if self.model is None:
            self.load_model()

        logger.debug(f"Starting transcription for file: {file_path}")
        try:
            segments, _ = self.model.transcribe(
                file_path,
                task="transcribe",
                without_timestamps=True,
                beam_size=1,
                language="ru",
                condition_on_previous_text=False,
            )

            # Combine text segments
            transcription = " ".join([segment.text for segment in segments])
            logger.info(f"Transcription completed successfully for file: {file_path}")
            return transcription
        except Exception as e:
            logger.exception(f"Transcription failed for file {file_path}: {e}")
            raise
