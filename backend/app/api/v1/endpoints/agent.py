from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str

@router.post("/agent", response_model=QueryResponse)
async def interact_with_agent(request: QueryRequest):
    # Здесь будет логика взаимодействия с агентом
    response = f"Received query: {request.query}"
    return QueryResponse(response=response)