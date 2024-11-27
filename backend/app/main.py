# backend/app/main.py

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel
import torch
import logging

from .core.config import settings
from .core.logging_config import setup_logging
from .api.v1.api import api_router
from .services.redis_service import RedisService


class KonspectoAPIApp:
    def __init__(self):
        setup_logging()
        self.logger = logging.getLogger("app.main")
        self.logger.info("Initializing KONSPECTO API...")

        self.app = FastAPI(
            title=settings.PROJECT_NAME,
            description="Backend API for KONSPECTO application",
            version=settings.PROJECT_VERSION,
        )

        self._setup_middleware()
        self._setup_services()
        self._setup_event_handlers()
        self._setup_routes()

        self.logger.info("KONSPECTO API initialized successfully.")

    def _setup_middleware(self):
        """Настройка промежуточного программного обеспечения (middleware)."""
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
        """Настройка событий запуска и остановки приложения."""
        self.app.add_event_handler("startup", self._startup_event)
        self.app.add_event_handler("shutdown", self._shutdown_event)

    async def _startup_event(self):
        """Событие, выполняемое при запуске приложения."""
        self.logger.info("Starting up: Connecting to Redis...")
        await self.redis_service.connect()
        self.logger.info("Starting up: Loading Whisper model...")
        try:
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if torch.cuda.is_available() else "float32"
            cpu_threads = 8
            self.app.state.whisper_model = WhisperModel(
                "large-v3",
                device=device,
                compute_type=compute_type,
                cpu_threads=cpu_threads
            )
            self.logger.info("Whisper model loaded successfully.")
        except Exception as e:
            self.logger.exception("Failed to load Whisper model.")
            raise

    async def _shutdown_event(self):
        """Событие, выполняемое при остановке приложения."""
        self.logger.info("Shutting down: Closing Redis connection...")
        await self.redis_service.close()

    def _setup_routes(self):
        """Настройка маршрутов приложения."""
        self.app.add_api_route("/", self._root_endpoint, methods=["GET"], tags=["Root"])
        self.app.add_api_route("/health", self._health_check_endpoint, methods=["GET"], tags=["Health"])

        # Включение API Router с зависимостью
        self.app.include_router(
            api_router,
            prefix="/api",
            dependencies=[Depends(self._get_redis_service)]
        )

    async def _root_endpoint(self):
        """Корневой эндпоинт приложения."""
        return {"message": "Welcome to KONSPECTO API"}

    async def _health_check_endpoint(self) -> dict:
        """Эндпоинт для проверки состояния приложения."""
        try:
            redis_ok = await self.redis_service.exists_key("health_check")
            status = "healthy" if redis_ok else "unhealthy"
            return {
                "status": status,
                "version": settings.PROJECT_VERSION,
                "redis_connected": redis_ok
            }
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "version": settings.PROJECT_VERSION,
                "redis_connected": False,
                "error": str(e)
            }

    def get_app(self) -> FastAPI:
        """Возвращает экземпляр FastAPI приложения."""
        return self.app


app_instance = KonspectoAPIApp()
app = app_instance.get_app()