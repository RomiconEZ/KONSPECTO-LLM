from pydantic import BaseModel, Field


class TranscriptionResponse(BaseModel):
    """
    Модель ответа транскрипции.
    """

    transcription: str = Field(..., examples=["Это пример транскрибированного текста."])
