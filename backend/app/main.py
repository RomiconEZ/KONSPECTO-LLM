# backend/app/main.py
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting up: Connecting to Redis...")
        await redis_service.connect()

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

    # Include API Router
    app.include_router(api_router, prefix="/api")

    logger.info("KONSPECTO API initialized successfully.")
    return app

app = create_application()