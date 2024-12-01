# KONSPECTO/backend/app/main.py

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel
import torch
import logging

from .core.config import get_settings  # Updated import
from .core.logging_config import setup_logging
from .api.v1.api import api_router
from .services.redis_service import RedisService
from .services.index_service import get_query_engine  # Added import

class KonspectoAPIApp:
    def __init__(self):
        setup_logging()
        self.logger = logging.getLogger("app.main")
        self.logger.info("Initializing KONSPECTO API...")

        self.app = FastAPI(
            title=get_settings().PROJECT_NAME,
            description="Backend API for KONSPECTO application",
            version=get_settings().PROJECT_VERSION,
        )

        self._setup_middleware()
        self._setup_services()
        self._setup_event_handlers()
        self._setup_routes()

        self.logger.info("KONSPECTO API initialized successfully.")

    def _setup_middleware(self):
        """Setup middleware."""
        settings = get_settings()
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_services(self):
        """Initialize services such as Redis."""
        self.redis_service = RedisService()

    def _get_redis_service(self):
        """Dependency to retrieve RedisService instance."""
        return self.redis_service

    def _setup_event_handlers(self):
        """Setup startup and shutdown event handlers."""
        self.app.add_event_handler("startup", self._startup_event)
        self.app.add_event_handler("shutdown", self._shutdown_event)

    async def _startup_event(self):
        """Event handler executed on application startup."""
        self.logger.info("Starting up: Connecting to Redis...")
        await self.redis_service.connect()
        self.logger.info("Starting up: Loading Whisper model...")
        try:
            settings = get_settings()
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if torch.cuda.is_available() else "float32"
            cpu_threads = 8
            model_size_large = "large-v3"
            model_size_small = "medium"
            self.app.state.whisper_model = WhisperModel(
                model_size_small,
                device=device,
                # compute_type=compute_type,
                cpu_threads=cpu_threads
            )
            self.logger.info("Whisper model loaded successfully.")

            # Initialize query engine during startup
            self.logger.info("Initializing query engine...")
            query_engine = get_query_engine()
            # Optionally store it in app.state if needed elsewhere
            self.app.state.query_engine = query_engine
            self.logger.info("Query engine initialized successfully.")
        except Exception as e:
            self.logger.exception("Failed to load Whisper model or initialize query engine.")
            raise

    async def _shutdown_event(self):
        """Event handler executed on application shutdown."""
        self.logger.info("Shutting down: Closing Redis connection...")
        await self.redis_service.close()

    def _setup_routes(self):
        """Setup application routes."""
        self.app.add_api_route("/", self._root_endpoint, methods=["GET"], tags=["Root"])
        self.app.add_api_route("/health", self._health_check_endpoint, methods=["GET"], tags=["Health"])

        # Include API Router with dependency
        self.app.include_router(
            api_router,
            prefix="/api",
            dependencies=[Depends(self._get_redis_service)]
        )

    async def _root_endpoint(self):
        """Root endpoint of the application."""
        return {"message": "Welcome to KONSPECTO API"}

    async def _health_check_endpoint(self) -> dict:
        """Endpoint to check the health of the application."""
        try:
            redis_ok = await self.redis_service.exists_key("health_check")
            status = "healthy" if redis_ok else "unhealthy"
            return {
                "status": status,
                "version": get_settings().PROJECT_VERSION,
                "redis_connected": redis_ok
            }
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "version": get_settings().PROJECT_VERSION,
                "redis_connected": False,
                "error": str(e)
            }

    def get_app(self) -> FastAPI:
        """Returns the FastAPI application instance."""
        return self.app


app_instance = KonspectoAPIApp()
app = app_instance.get_app()