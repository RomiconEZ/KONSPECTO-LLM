# KONSPECTO/backend/app/models/transcription.py

from pydantic import BaseModel, Field

class TranscriptionResponse(BaseModel):
    """
    Модель ответа транскрипции.
    """
    transcription: str = Field(..., example="Это пример транскрибированного текста.")