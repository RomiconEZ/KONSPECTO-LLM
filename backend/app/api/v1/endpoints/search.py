# backend/app/api/v1/endpoints/search.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

router = APIRouter()


class SearchRequest(BaseModel):
    query: str


class SearchResult(BaseModel):
    full_result: str
    abbreviated_result: str
    source: str


@router.post("/search", response_model=SearchResult)
async def search_documents(request: SearchRequest):
    # Загрузка документов и создание индекса
    documents = SimpleDirectoryReader('path/to/documents').load_data()
    index = VectorStoreIndex.from_documents(documents)

    # Выполнение поиска
    response = index.query(request.query)

    # Формирование результатов
    full_result = response['full_result']
    abbreviated_result = response['abbreviated_result']
    source = response['source']

    return SearchResult(
        full_result=full_result,
        abbreviated_result=abbreviated_result,
        source=source
    )