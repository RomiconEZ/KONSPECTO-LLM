# KONSPECTO/backend/app/main.py

from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel
import torch
import logging

from .core.config import get_settings  # Обновленный импорт
from .core.logging_config import setup_logging
from .api.v1.api import api_router
from .services.redis_service import RedisService
from .services.index_service import get_query_engine  # Добавленный импорт

# Новые импорты для моделей транскрибации
from .services.transcription.base import AbstractTranscriptionModel
from .services.transcription.whisper_model import WhisperTranscriptionModel

class KonspectoAPIApp:
    def __init__(self):
        setup_logging()
        self.logger = logging.getLogger("app.main")
        self.logger.info("Инициализация KONSPECTO API...")

        self.app = FastAPI(
            title=get_settings().PROJECT_NAME,
            description="Backend API для приложения KONSPECTO",
            version=get_settings().PROJECT_VERSION,
        )

        self._setup_middleware()
        self._setup_services()
        self._setup_event_handlers()
        self._setup_routes()

        self.logger.info("KONSPECTO API успешно инициализировано.")

    def _setup_middleware(self):
        """Настройка middleware."""
        settings = get_settings()
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_services(self):
        """Инициализация сервисов, таких как Redis."""
        self.redis_service = RedisService()

    def _get_redis_service(self):
        """Зависимость для получения экземпляра RedisService."""
        return self.redis_service

    def _setup_event_handlers(self):
        """Настройка обработчиков событий старта и остановки."""
        self.app.add_event_handler("startup", self._startup_event)
        self.app.add_event_handler("shutdown", self._shutdown_event)

    async def _startup_event(self):
        """Обработчик события запуска приложения."""
        self.logger.info("Запуск: Подключение к Redis...")
        await self.redis_service.connect()
        self.logger.info("Запуск: Инициализация модели транскрибации...")

        settings = get_settings()

        # Инициализация выбранной модели транскрибации на основе настроек
        try:
            transcription_model_name = settings.TRANSCRIPTION_MODEL.lower()
            if transcription_model_name == "whisper":
                transcription_model = WhisperTranscriptionModel()
                transcription_model.load_model()
                self.app.state.transcription_model = transcription_model
                self.logger.info(f"Модель транскрибации '{transcription_model_name}' успешно загружена.")
            else:
                self.logger.error(f"Неизвестная модель транскрибации: {transcription_model_name}")
                raise ValueError(f"Неизвестная модель транскрибации: {transcription_model_name}")
        except Exception as e:
            self.logger.exception("Не удалось инициализировать модель транскрибации.")
            raise

        # Инициализация query engine при запуске
        self.logger.info("Инициализация query engine...")
        query_engine = get_query_engine()
        # При необходимости можно сохранить его в app.state для использования в других местах
        self.app.state.query_engine = query_engine
        self.logger.info("Query engine успешно инициализирован.")

    async def _shutdown_event(self):
        """Обработчик события остановки приложения."""
        self.logger.info("Остановка: Закрытие соединения с Redis...")
        await self.redis_service.close()

    def _setup_routes(self):
        """Настройка маршрутов приложения."""
        self.app.add_api_route("/", self._root_endpoint, methods=["GET"], tags=["Root"])
        self.app.add_api_route("/health", self._health_check_endpoint, methods=["GET"], tags=["Health"])

        # Включение API Router без глобальных зависимостей
        self.app.include_router(
            api_router,
            prefix="/api",
            dependencies=[]  # Зависимости устанавливаются в отдельных эндпойнтах
        )

    async def _root_endpoint(self):
        """Корневой эндпойнт приложения."""
        return {"message": "Добро пожаловать в KONSPECTO API"}

    async def _health_check_endpoint(self) -> dict:
        """Эндпойнт для проверки состояния приложения."""
        try:
            redis_ok = await self.redis_service.exists_key("health_check")
            status = "healthy" if redis_ok else "unhealthy"
            return {
                "status": status,
                "version": get_settings().PROJECT_VERSION,
                "redis_connected": redis_ok
            }
        except Exception as e:
            self.logger.error(f"Проверка состояния не удалась: {e}")
            return {
                "status": "unhealthy",
                "version": get_settings().PROJECT_VERSION,
                "redis_connected": False,
                "error": str(e)
            }

    def get_app(self) -> FastAPI:
        """Возвращает экземпляр FastAPI приложения."""
        return self.app


app_instance = KonspectoAPIApp()
app = app_instance.get_app()