# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.redis_service import redis_service


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

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to KONSPECTO API"}

@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    redis_ok = await redis_service.exists_key("health_check")
    return {
        "status": "healthy",
        "version": app.version,
        "redis_connected": redis_ok
    }