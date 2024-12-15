# KONSPECTO/backend/app/api/v1/endpoints/agent.py

import logging

from functools import lru_cache
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from langchain_community.chat_models import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, Field

from agent.react_agent import ReactAgent  # Импортируем ReactAgent
from app.core.config import Settings, get_settings
from app.services.llm.llm_studio_client import LLMStudioClient

router = APIRouter()
logger = logging.getLogger("app.api.v1.endpoints.agent")


class QueryRequest(BaseModel):
    """
    Модель запроса для взаимодействия с агентом.
    """

    query: str = Field(
        "Градиентный спуск и преобразование Фурье",
        example="Градиентный спуск и преобразование Фурье",
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

    def __init__(self, agent: ReactAgent):
        """
        Инициализация сервисного класса агента.
        """
        self.agent = agent  # Инициализируем ReactAgent

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
                logger.error(
                    f"Expected response to be a string, got {type(response)} instead."
                )
                raise HTTPException(
                    status_code=500, detail="Invalid response type from agent."
                )
            # Дополнительная валидация или обработка может быть добавлена здесь
            return response
        except HTTPException as he:
            # Передача HTTPException без изменений
            raise he
        except Exception as e:
            logger.exception("Failed to process query.")
            raise HTTPException(status_code=500, detail=str(e))


# Probably better to use DI container for this (e.g. wireup)
# https://maldoinc.github.io/wireup/0.14.0/integrations/fastapi/
def get_llm_client(
    settings: Annotated[Settings, Depends(get_settings)],
) -> BaseChatModel:
    if settings.OPENAI_API_URL:
        assert settings.MODEL_NAME is not None
        return ChatOpenAI(
            model=settings.MODEL_NAME,
            base_url=settings.OPENAI_API_URL,
            api_key=settings.OPENAI_API_KEY,
        )
    else:
        return LLMStudioClient()


def get_react_agent(
    llm_client: Annotated[BaseChatModel, Depends(get_llm_client)]
) -> ReactAgent:
    return ReactAgent(llm_client)


@lru_cache
def get_agent_service(react_agent: Annotated[ReactAgent, Depends(get_react_agent)]):
    return AgentService(react_agent)


@router.post("/", response_model=QueryResponse)
async def interact_with_agent(
    request: QueryRequest,
    agent_service: Annotated[AgentService, Depends(get_agent_service)],
):
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
