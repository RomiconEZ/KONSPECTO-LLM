# KONSPECTO/backend/app/core/config.py
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, Field
from typing import List
from pathlib import Path
from functools import lru_cache

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
    GOOGLE_SERVICE_ACCOUNT_KEY_PATH: str = Field(
        "config/service_account_key.json", env="GOOGLE_SERVICE_ACCOUNT_KEY_PATH"
    )

    class Config:
        # Set the env_file path to the new location
        env_file = Path(__file__).resolve().parent.parent / "config/.env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()