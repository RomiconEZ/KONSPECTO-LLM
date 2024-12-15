# KONSPECTO/backend/app/core/config.py

import logging
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import AnyHttpUrl, Field, validator
from pydantic_settings import BaseSettings

# Logging configuration for the config module
logger = logging.getLogger("app.core.config")
logger.setLevel(logging.DEBUG)  # Set the desired logging level


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
        env="GOOGLE_SERVICE_ACCOUNT_KEY_PATH",
    )

    # Transcription Model Configuration
    TRANSCRIPTION_MODEL: str = Field(default="whisper", env="TRANSCRIPTION_MODEL")

    # LLM Studio Base URL Configuration
    LLM_STUDIO_BASE_URL: str = Field(
        default="http://localhost:1234/v1",
        env="LLM_STUDIO_BASE_URL",
        description="Base URL for the LLM Studio API.",
    )

    # Embedding Model Configuration
    EMBEDDING_MODEL_NAME: str = Field(
        default="intfloat/multilingual-e5-large",
        env="EMBEDDING_MODEL_NAME",
        description="Name of the embedding model to use in HuggingFaceEmbedding.",
    )

    # Embedding Batch Size configuration
    EMBEDDING_BATCH_SIZE: int = Field(
        default=16,
        env="EMBEDDING_BATCH_SIZE",
        description="Batch size for embeddings in HuggingFaceEmbedding.",
    )

    # Whisper Model Size configuration
    WHISPER_MODEL_SIZE: str = Field(
        default="large-v2",
        env="WHISPER_MODEL_SIZE",
        description="Size of the Whisper model to use for transcription.",
    )

    # Embedding Dimension Configuration
    EMBEDDING_DIMENSION: int = Field(
        default=1024,
        env="EMBEDDING_DIMENSION",
        description="Dimensions of the embedding vectors.",
    )

    @validator("GOOGLE_SERVICE_ACCOUNT_KEY_PATH", pre=True)
    def validate_service_account_path(cls, v):
        logger.debug(f"Original GOOGLE_SERVICE_ACCOUNT_KEY_PATH value: {v}")
        path = Path(v)
        if not path.is_absolute():
            # Resolve relative path relative to the configuration directory
            resolved_path = (Path(__file__).resolve().parent.parent / path).resolve()
            logger.debug(f"Resolved relative path to: {resolved_path}")
            path = resolved_path
        else:
            logger.debug(f"Provided path is absolute: {path}")

        if not path.exists():
            logger.warning(f"GOOGLE_SERVICE_ACCOUNT_KEY_PATH does not exist: {path}")
        else:
            logger.debug(f"GOOGLE_SERVICE_ACCOUNT_KEY_PATH exists: {path}")
        return path

    class Config:
        # Set the path to the .env file
        env_file = (
            Path(__file__).resolve().parent.parent / "config" / ".env"
        ).as_posix()
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
    logger.debug(
        f"GOOGLE_SERVICE_ACCOUNT_KEY_PATH: {settings.GOOGLE_SERVICE_ACCOUNT_KEY_PATH}"
    )
    logger.debug(f"TRANSCRIPTION_MODEL: {settings.TRANSCRIPTION_MODEL}")
    logger.debug(f"LLM_STUDIO_BASE_URL: {settings.LLM_STUDIO_BASE_URL}")
    logger.debug(f"EMBEDDING_MODEL_NAME: {settings.EMBEDDING_MODEL_NAME}")
    logger.debug(f"EMBEDDING_BATCH_SIZE: {settings.EMBEDDING_BATCH_SIZE}")
    logger.debug(f"WHISPER_MODEL_SIZE: {settings.WHISPER_MODEL_SIZE}")
    logger.debug(f"EMBEDDING_DIMENSION: {settings.EMBEDDING_DIMENSION}")
    return settings