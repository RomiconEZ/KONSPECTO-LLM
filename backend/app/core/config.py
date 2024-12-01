# KONSPECTO/backend/app/core/config.py

from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, Field, validator
from typing import List
from pathlib import Path
from functools import lru_cache
import logging

# Настройка логирования для конфигурационного модуля
logger = logging.getLogger("app.core.config")
logger.setLevel(logging.DEBUG)  # Установите нужный уровень логирования

class Settings(BaseSettings):
    PROJECT_NAME: str = "KONSPECTO API"
    PROJECT_VERSION: str = "0.1.0"

    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:3000"]

    # Redis Configuration
    REDIS_URL: str = "redis://redis-stack:6379"

    # Chroma Configuration
    CHROMA_URL: str = "http://chroma:8000"

    # Google Drive Configuration
    FOLDER_ID: str = Field(..., env="FOLDER_ID")

    # Path to the service account key JSON file
    GOOGLE_SERVICE_ACCOUNT_KEY_PATH: Path = Field(
        default=Path("config/service_account_key.json"),
        env="GOOGLE_SERVICE_ACCOUNT_KEY_PATH"
    )

    # Transcription Model Configuration
    TRANSCRIPTION_MODEL: str = Field(default="whisper", env="TRANSCRIPTION_MODEL")

    # Новая переменная конфигурации для LLMStudioClient
    LLM_STUDIO_BASE_URL: str = Field(
        default="http://localhost:1234/v1",
        env="LLM_STUDIO_BASE_URL",
        description="Базовый URL для LLM Studio API."
    )

    @validator('GOOGLE_SERVICE_ACCOUNT_KEY_PATH', pre=True)
    def validate_service_account_path(cls, v):
        logger.debug(f"Original GOOGLE_SERVICE_ACCOUNT_KEY_PATH value: {v}")
        path = Path(v)
        if not path.is_absolute():
            # Разрешение относительного пути относительно директории конфигурации
            resolved_path = (Path(__file__).resolve().parent.parent / path).resolve()
            logger.debug(f"Resolved relative path to: {resolved_path}")
            path = resolved_path
        else:
            logger.debug(f"Provided path is absolute: {path}")

        if not path.exists():
            logger.warning(
                f"GOOGLE_SERVICE_ACCOUNT_KEY_PATH does not exist: {path}"
            )
        else:
            logger.debug(
                f"GOOGLE_SERVICE_ACCOUNT_KEY_PATH exists: {path}"
            )
        return path

    class Config:
        # Устанавливаем путь к файлу окружения .env
        env_file = (Path(__file__).resolve().parent.parent / "config" / ".env").as_posix()
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    logger.debug("Settings loaded successfully.")
    logger.debug(f"PROJECT_NAME: {settings.PROJECT_NAME}")
    logger.debug(f"PROJECT_VERSION: {settings.PROJECT_VERSION}")
    logger.debug(f"REDIS_URL: {settings.REDIS_URL}")
    logger.debug(f"CHROMA_URL: {settings.CHROMA_URL}")
    logger.debug(f"FOLDER_ID: {settings.FOLDER_ID}")
    logger.debug(f"GOOGLE_SERVICE_ACCOUNT_KEY_PATH: {settings.GOOGLE_SERVICE_ACCOUNT_KEY_PATH}")
    logger.debug(f"TRANSCRIPTION_MODEL: {settings.TRANSCRIPTION_MODEL}")
    logger.debug(f"LLM_STUDIO_BASE_URL: {settings.LLM_STUDIO_BASE_URL}")
    return settings