# backend/app/api/v1/endpoints/search.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
from ....services.index_service import query_engine

# Настройка логирования
logger = logging.getLogger(__name__)

router = APIRouter()

# Импорт перечислений для фиксированных значений
from enum import Enum

# Перечисление типов объектов
class ObjectType(str, Enum):
    DOCUMENT = "4"  # Тип объекта: Документ

# Перечисление типов отношений между узлами
class NodeRelationship(str, Enum):
    SOURCE = "1"  # Тип отношения: Источник

# Модель информации о связанном узле
class RelatedNodeInfo(BaseModel):
    node_id: str  # Идентификатор связанного узла
    node_type: ObjectType  # Тип связанного узла
    metadata: Dict[str, Any]  # Метаданные связанного узла
    hash: str  # Хеш связанного узла

# Модель текстового узла
class TextNode(BaseModel):
    id_: str  # Идентификатор узла
    embedding: Optional[Any]  # Встраивание узла (может быть любым типом, уточните при необходимости)
    metadata: Dict[str, Any]  # Метаданные узла
    excluded_embed_metadata_keys: List[str]  # Ключи метаданных, исключенные из встраивания
    excluded_llm_metadata_keys: List[str]  # Ключи метаданных, исключенные из обработки LLM
    relationships: Dict[NodeRelationship, RelatedNodeInfo]  # Отношения с другими узлами
    text: str  # Текстовое содержимое узла
    mimetype: str  # MIME-тип содержимого узла
    start_char_idx: int  # Начальный индекс символа в тексте
    end_char_idx: int  # Конечный индекс символа в тексте
    text_template: str  # Шаблон для формирования текста
    metadata_template: str  # Шаблон для формирования метаданных
    metadata_seperator: str  # Разделитель метаданных

# Модель узла с оценкой релевантности
class NodeWithScore(BaseModel):
    node: TextNode  # Объект TextNode
    score: float  # Оценка релевантности узла

# Модель запроса поиска
class SearchRequest(BaseModel):
    query: str  # Текстовый запрос для поиска

# Новая модель для отдельных результатов поиска
class SearchItem(BaseModel):
    modified_at: datetime  # Дата последнего изменения файла
    file_name: str  # Название файла
    file_id: str  # Идентификатор файла
    text: str  # Текстовое содержимое
    score: float  # Оценка релевантности
    start_char_idx: int  # Начальный индекс символа в тексте
    end_char_idx: int  # Конечный индекс символа в тексте

# Обновленная модель результата поиска
class SearchResult(BaseModel):
    results: List[SearchItem]  # Список результатов поиска

@router.post("/search", response_model=SearchResult)
async def search_documents(request: SearchRequest):
    """
    Эндпоинт для поиска документов по заданному запросу.

    :param request: Объект SearchRequest с полем 'query' содержащим строку запроса.
    :return: Объект SearchResult с результатами поиска.
    """
    try:
        # Выполнение поиска с помощью движка запросов
        response = query_engine.query(request.query)

        # Логирование получения ответа от движка поиска
        logger.info("Получен ответ от движка поиска.")

        # Логирование каждого отдельного поля ответа
        full_response = response.response  # Полный ответ на запрос
        logger.debug(f"Полный ответ ('response'): {full_response}")

        source_nodes = response.source_nodes  # Список исходных узлов
        logger.debug(f"Исходные узлы ('source_nodes'): {source_nodes}")

        metadata = response.metadata  # Метаданные ответа
        logger.debug(f"Метаданные ('metadata'): {metadata}")

        # Дополнительное логирование полей внутри source_nodes
        for idx, node_with_score in enumerate(source_nodes, start=1):
            score = node_with_score.score  # Извлечение оценки релевантности
            logger.debug(f"Исходный узел {idx} - Оценка ('score'): {score}")

            node = node_with_score.node  # Извлечение узла
            if node:
                logger.debug(f"Исходный узел {idx} - Узел ('node'):")
                logger.debug(f"  ID: {node.id_}")
                logger.debug(f"  Встраивание ('embedding'): {node.embedding}")
                logger.debug(f"  Метаданные ('metadata'): {node.metadata}")
                logger.debug(f"  Исключенные ключи метаданных для встраивания: {node.excluded_embed_metadata_keys}")
                logger.debug(f"  Исключенные ключи метаданных для LLM: {node.excluded_llm_metadata_keys}")
                logger.debug(f"  Отношения ('relationships'): {node.relationships}")
                logger.debug(f"  Текст ('text'): {node.text}")
                logger.debug(f"  MIME-тип ('mimetype'): {node.mimetype}")
                logger.debug(f"  Начальный индекс символа ('start_char_idx'): {node.start_char_idx}")
                logger.debug(f"  Конечный индекс символа ('end_char_idx'): {node.end_char_idx}")
                logger.debug(f"  Шаблон текста ('text_template'): {node.text_template}")
                logger.debug(f"  Шаблон метаданных ('metadata_template'): {node.metadata_template}")
                logger.debug(f"  Разделитель метаданных ('metadata_seperator'): {node.metadata_seperator}")

        # Преобразование исходных узлов в список объектов SearchItem
        search_items = []
        for node_with_score in source_nodes:
            node = node_with_score.node  # Извлечение узла
            score = node_with_score.score  # Извлечение оценки релевантности
            if node:
                metadata = node.metadata

                # Извлечение необходимых метаданных
                modified_at_str = metadata.get('modified at')
                file_name = metadata.get('file name') or metadata.get('file_name', '')
                file_id = metadata.get('file id', '')

                # Проверка наличия необходимых полей
                if not all([modified_at_str, file_name, file_id]):
                    logger.warning(f"Недостаточно данных для узла с ID: {node.id_}")
                    continue  # Пропустить этот узел, если данные неполные

                # Преобразование строки даты в объект datetime
                try:
                    modified_at = datetime.fromisoformat(modified_at_str.replace('Z', '+00:00'))
                except ValueError as ve:
                    logger.error(f"Неверный формат даты для узла с ID: {node.id_}: {modified_at_str}", exc_info=True)
                    continue  # Пропустить этот узел, если дата некорректна

                # Создание объекта SearchItem
                search_item = SearchItem(
                    modified_at=modified_at,
                    file_name=file_name,
                    file_id=file_id,
                    text=node.text,
                    score=score,
                    start_char_idx=node.start_char_idx,
                    end_char_idx=node.end_char_idx
                )
                search_items.append(search_item)

        # Формирование итогового результата поиска
        search_result = SearchResult(results=search_items)

        # Логирование информации о запросе и результате поиска
        logger.info(f"Запрос поиска: {request.query}")
        logger.info(f"Количество результатов: {len(search_items)}")

        return search_result
    except Exception as e:
        # Логирование ошибки с трассировкой стека
        logger.error(f"Поиск не удался: {e}", exc_info=True)
        # Возвращение HTTP-исключения с кодом 500
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")