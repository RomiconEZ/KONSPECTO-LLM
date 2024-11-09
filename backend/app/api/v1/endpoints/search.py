# backend/app/api/v1/endpoints/search.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from ....services.index_service import query_engine

# Настройка логирования
logger = logging.getLogger(__name__)

router = APIRouter()


class SearchRequest(BaseModel):
    query: str


class SearchResult(BaseModel):
    full_result: str
    abbreviated_result: str
    source: str


@router.post("/search", response_model=SearchResult)
async def search_documents(request: SearchRequest):
    try:
        # Выполнение поиска
        response = query_engine.query(request.query)

        search_result = SearchResult(
            full_result=str(response),
            abbreviated_result=str(response),
            source=""
        )

        # Логирование результатов поиска
        logger.info(f"Search query: {request.query}")
        logger.info(f"Search result: {search_result}")

        return search_result
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))