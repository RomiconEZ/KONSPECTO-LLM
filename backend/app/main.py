# backend/app/main.py
import logging
from .logging_config import setup_logging

# Настройка логирования
setup_logging()
logger = logging.getLogger(__name__)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.api import api_router
from .services.redis_service import RedisService


logger.info("Starting KONSPECTO API...")

app = FastAPI(
    title="KONSPECTO API",
    description="Backend API for KONSPECTO application",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_service = RedisService()

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to KONSPECTO API"}

@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    try:
        redis_ok = await redis_service.exists_key("health_check")
        return {
            "status": "healthy",
            "version": app.version,
            "redis_connected": redis_ok
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "version": app.version,
            "redis_connected": False,
            "error": str(e)
        }

@app.on_event("startup")
async def startup_event():
    try:
        await redis_service.connect()
        logger.info("Connected to Redis successfully.")
    except Exception as e:
        logger.error(f"Failed to connect to Redis on startup: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    await redis_service.close()
    logger.info("Redis connection closed.")

app.include_router(api_router)

logger.info("KONSPECTO API started successfully.")