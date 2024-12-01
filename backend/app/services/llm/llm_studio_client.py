# KONSPECTO/backend/app/services/llm/llm_studio_client.py

from typing import ClassVar
from langchain_community.chat_models import ChatOpenAI
from app.core.config import get_settings  # Импортируем функцию для получения настроек


class LLMStudioClient(ChatOpenAI):
    """
    Клиент для взаимодействия с LLM Studio через интерфейс ChatOpenAI из библиотеки LangChain.

    Args:
        temperature (float, optional): Температура сэмплирования. По умолчанию 0.3.
        max_tokens (int, optional): Максимальное количество генерируемых токенов. По умолчанию None.
        model (str, optional): Название модели. По умолчанию "local".
        timeout (float, optional): Тайм-аут запроса в секундах. По умолчанию None.
        max_retries (int, optional): Максимальное количество повторных попыток при неудачных запросах. По умолчанию 1.
        **kwargs: Дополнительные именованные аргументы, передаваемые в ChatOpenAI.
    """

    DEFAULT_API_KEY: ClassVar[str] = "lm-studio"

    def __init__(
            self,
            temperature: float = 0.3,
            max_tokens: int = None,
            model: str = "local",
            timeout: float = None,
            max_retries: int = 1,
            **kwargs
    ):
        settings = get_settings()
        base_url = settings.LLM_STUDIO_BASE_URL

        super().__init__(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            max_retries=max_retries,
            api_key=self.DEFAULT_API_KEY,
            base_url=base_url,
            **kwargs
        )