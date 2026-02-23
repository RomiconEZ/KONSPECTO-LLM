# KONSPECTO/backend/app/api/v1/endpoints/agent.py

import logging
from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from agent.react_agent import ReactAgent

router = APIRouter()
logger = logging.getLogger("app.api.v1.endpoints.agent")


class QueryRequest(BaseModel):
    """
    Модель запроса для взаимодействия с агентом.
    """

    query: str = Field(
        "Градиентный спуск и преобразование Фурье",
        examples=["Градиентный спуск и преобразование Фурье"],
    )


class QueryResponse(BaseModel):
    """
    Модель ответа от агента.
    """

    response: str


class AgentService:
    """
    Сервисный класс для обработки запросов агента.
    """

    def __init__(self):
        """
        Инициализация сервисного класса агента.
        """
        self.agent = ReactAgent()

    async def process_query(self, query: str) -> str:
        """
        Асинхронная обработка запроса к агенту и получение ответа.

        :param query: Строка запроса от пользователя.
        :return: Ответ агента в виде строки.
        """
        logger.debug(f"Processing query: {query}")
        try:
            response = await self.agent.ainvoke(query)
            logger.debug(f"Agent response: {response}")
            return response
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Failed to process query: {query}")
            raise HTTPException(status_code=500, detail=str(e))


@lru_cache()
def get_agent_service() -> AgentService:
    """
    Factory function with lazy singleton initialization for AgentService.

    :return: Cached AgentService instance.
    """
    return AgentService()


@router.post("/", response_model=QueryResponse)
async def interact_with_agent(
    request: QueryRequest,
    agent_service: AgentService = Depends(get_agent_service),
):
    """
    Эндпойнт для взаимодействия с агентом.

    :param request: Объект запроса QueryRequest с полем query.
    :param agent_service: Экземпляр AgentService, внедрённый через Depends.
    :return: Объект ответа QueryResponse с полем response.
    """
    response = await agent_service.process_query(request.query)
    return QueryResponse(response=response)
