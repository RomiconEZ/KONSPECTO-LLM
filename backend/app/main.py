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


def create_application() -> FastAPI:
    setup_logging()
    logger = logging.getLogger("app.main")
    logger.info("Initializing KONSPECTO API...")

    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Backend API for KONSPECTO application",
        version=settings.PROJECT_VERSION,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize services
    redis_service = RedisService()

    # Define a dependency function
    def get_redis_service():
        return redis_service

    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting up: Connecting to Redis...")
        await redis_service.connect()
        logger.info("Starting up: Loading Whisper model...")
        try:
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if torch.cuda.is_available() else "float32"
            cpu_threads = 8
            app.state.whisper_model = WhisperModel(
                "large-v3",
                device=device,
                compute_type=compute_type,
                cpu_threads=cpu_threads
            )
            logger.info("Whisper model loaded successfully.")
        except Exception as e:
            logger.exception("Failed to load Whisper model.")
            raise

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down: Closing Redis connection...")
        await redis_service.close()

    @app.get("/", tags=["Root"])
    async def root():
        return {"message": "Welcome to KONSPECTO API"}

    @app.get("/health", tags=["Health"])
    async def health_check() -> dict:
        try:
            redis_ok = await redis_service.exists_key("health_check")
            status = "healthy" if redis_ok else "unhealthy"
            return {
                "status": status,
                "version": settings.PROJECT_VERSION,
                "redis_connected": redis_ok
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "version": settings.PROJECT_VERSION,
                "redis_connected": False,
                "error": str(e)
            }

    # Include API Router with the dependency
    app.include_router(
        api_router,
        prefix="/api",
        dependencies=[Depends(get_redis_service)]
    )

    logger.info("KONSPECTO API initialized successfully.")
    return app


app = create_application()
