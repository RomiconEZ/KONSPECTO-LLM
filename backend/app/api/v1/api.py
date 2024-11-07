# backend/app/api/v1/api.py
from fastapi import APIRouter
from app.api.v1.endpoints import agent, search

api_router = APIRouter()
api_router.include_router(agent.router, prefix="/v1", tags=["agent"])
api_router.include_router(search.router, prefix="/v1", tags=["search"])