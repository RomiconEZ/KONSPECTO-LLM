# KONSPECTO/backend/app/api/v1/endpoints/agent.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import logging

from agent.react_agent import ReactAgent  # Импортируем ReactAgent

router = APIRouter()
logger = logging.getLogger("app.api.v1.endpoints.agent")


class QueryRequest(BaseModel):
    """
    Модель запроса для взаимодействия с агентом.
    """
    query: str = Field("Градиентный спуск и преобразование Фурье", example="Градиентный спуск и преобразование Фурье")


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
        self.agent = ReactAgent()  # Инициализируем ReactAgent

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
            if not isinstance(response, str):
                logger.error(f"Expected response to be a string, got {type(response)} instead.")
                raise HTTPException(status_code=500, detail="Invalid response type from agent.")
            # Дополнительная валидация или обработка может быть добавлена здесь
            return response
        except HTTPException as he:
            # Передача HTTPException без изменений
            raise he
        except Exception as e:
            logger.exception("Failed to process query.")
            raise HTTPException(status_code=500, detail=str(e))


# Инициализация сервисного класса агента
agent_service = AgentService()


@router.post("/", response_model=QueryResponse)
async def interact_with_agent(request: QueryRequest):
    """
    Эндпойнт для взаимодействия с агентом.

    :param request: Объект запроса QueryRequest с полем query.
    :return: Объект ответа QueryResponse с полем response.
    """
    try:
        response = await agent_service.process_query(request.query)
        return QueryResponse(response=response)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("Agent interaction failed.")
        raise HTTPException(status_code=500, detail=str(e))