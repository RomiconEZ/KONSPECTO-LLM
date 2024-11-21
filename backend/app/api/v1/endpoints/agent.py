# backend/app/api/v1/endpoints/agent.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import logging

router = APIRouter()
logger = logging.getLogger("app.api.v1.endpoints.agent")

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str

@router.post("/", response_model=QueryResponse)
async def interact_with_agent(request: QueryRequest):
    """
    Endpoint to interact with the agent.
    """
    try:
        logger.debug(f"Agent received query: {request.query}")
        # Implement agent logic here
        response = f"Received query: {request.query}"
        logger.debug(f"Agent response: {response}")
        return QueryResponse(response=response)
    except Exception as e:
        logger.exception("Agent interaction failed.")
        raise HTTPException(status_code=500, detail="Internal Server Error")