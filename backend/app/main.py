# KONSPECTO/backend/app/main.py

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1.api import api_router
from .core.config import get_settings
from .core.logging_config import setup_logging
from .services.index_service import get_query_engine
from .services.redis_service import RedisService
from .services.transcription.whisper_model import WhisperTranscriptionModel


class KonspectoAPIApp:
    def __init__(self):
        setup_logging()
        self.logger = logging.getLogger("app.main")
        self.logger.info("Initializing KONSPECTO API...")

        self.app = FastAPI(
            title=get_settings().PROJECT_NAME,
            description="Backend API for the KONSPECTO application",
            version=get_settings().PROJECT_VERSION,
        )

        self._setup_middleware()
        self._setup_services()
        self._setup_event_handlers()
        self._setup_routes()

        self.logger.info("KONSPECTO API initialized successfully.")

    def _setup_middleware(self):
        """Set up middleware."""
        settings = get_settings()
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_services(self):
        """Initialize services such as Redis and store them in app state."""
        self.redis_service = RedisService()
        self.app.state.redis_service = self.redis_service

    def _setup_event_handlers(self):
        """Set up event handlers for startup and shutdown."""
        self.app.add_event_handler("startup", self._startup_event)
        self.app.add_event_handler("shutdown", self._shutdown_event)

    async def _startup_event(self):
        """Event handler for application startup."""
        self.logger.info("Startup: Connecting to Redis...")
        await self.redis_service.connect()
        self.logger.info("Startup: Initializing transcription model...")

        settings = get_settings()

        # Initialize the selected transcription model based on the settings
        transcription_model_name = settings.TRANSCRIPTION_MODEL.lower()
        if transcription_model_name == "whisper":
            transcription_model = WhisperTranscriptionModel(
                model_size=settings.WHISPER_MODEL_SIZE
            )
            transcription_model.load_model()
            self.app.state.transcription_model = transcription_model
            self.logger.info(
                f"Transcription model '{transcription_model_name}' loaded successfully."
            )
        else:
            self.logger.error(
                f"Unknown transcription model: {transcription_model_name}"
            )
            raise ValueError(f"Unknown transcription model: {transcription_model_name}")

        # Initialize query engine at startup
        self.logger.info("Initializing query engine...")
        query_engine = get_query_engine()
        self.app.state.query_engine = query_engine
        self.logger.info("Query engine initialized successfully.")

    async def _shutdown_event(self):
        """Event handler for application shutdown."""
        self.logger.info("Shutdown: Closing Redis connection...")
        await self.redis_service.close()

    def _setup_routes(self):
        """Set up application routes."""
        self.app.add_api_route("/", self._root_endpoint, methods=["GET"], tags=["Root"])
        self.app.add_api_route(
            "/health", self._health_check_endpoint, methods=["GET"], tags=["Health"]
        )

        # Include API Router without global dependencies
        self.app.include_router(
            api_router,
            prefix="/api",
            dependencies=[],
        )

    async def _root_endpoint(self):
        """Root endpoint of the application."""
        return {"message": "Добро пожаловать в KONSPECTO API"}

    async def _health_check_endpoint(self) -> dict:
        """Endpoint for checking the application's health."""
        try:
            redis_ping = await self.redis_service.redis_client.ping()
            redis_ok = redis_ping is True
            status = "healthy" if redis_ok else "unhealthy"

            return {
                "status": status,
                "version": get_settings().PROJECT_VERSION,
                "redis_connected": redis_ok,
            }
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "version": get_settings().PROJECT_VERSION,
                "redis_connected": False,
                "error": str(e),
            }

    def get_app(self) -> FastAPI:
        """Returns the FastAPI application instance."""
        return self.app


app_instance = KonspectoAPIApp()
app = app_instance.get_app()
