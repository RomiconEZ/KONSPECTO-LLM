# backend/app/api/v1/endpoints/search.py

from fastapi import APIRouter, HTTPException
import logging
from datetime import datetime
from typing import List

from ....services.index_service import get_query_engine  # Updated import
from ....models.search import SearchRequest, SearchResult, SearchItem

router = APIRouter()
logger = logging.getLogger("app.api.v1.endpoints.search")


class SearchService:
    """
    Сервисный класс для выполнения операций поиска.
    """

    @staticmethod
    def process_search(query: str) -> List[SearchItem]:
        """
        Обработка поискового запроса и возврат списка результатов поиска.

        :param query: Текстовый поисковый запрос.
        :return: Список объектов SearchItem с результатами поиска.
        """
        logger.debug(f"Processing search query: {query}")
        query_engine = get_query_engine()  # Use the function to get the query engine
        response = query_engine.query(query)
        logger.info("Received response from query engine.")

        # Log the full structure of the response for debugging
        logger.debug(f"Response structure: {response}")

        search_items = []
        for node_with_score in response.source_nodes:
            # Check if 'score' and 'node' attributes exist
            if hasattr(node_with_score, "score") and hasattr(node_with_score, "node"):
                score = node_with_score.score
                node = node_with_score.node
            else:
                logger.warning("node_with_score does not have 'score' or 'node' attributes.")
                continue

            if not node:
                logger.warning("Received node_with_score with no node.")
                continue

            metadata = node.metadata
            modified_at_str = metadata.get('modified_at') or metadata.get('modified at')
            file_name = metadata.get('file_name') or metadata.get('file name', '')
            file_id = metadata.get('file_id') or metadata.get('file id', '')

            # Ensure mandatory metadata fields are present
            if not all([modified_at_str, file_name, file_id]):
                logger.warning(f"Incomplete metadata for node ID: {node.id_}")
                continue

            try:
                modified_at = datetime.fromisoformat(modified_at_str.replace('Z', '+00:00'))
            except ValueError:
                logger.error(f"Invalid date format for node ID: {node.id_} - {modified_at_str}", exc_info=True)
                continue

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

        logger.info(f"Search query '{query}' returned {len(search_items)} results.")
        return search_items


@router.post("/", response_model=SearchResult)
async def search_documents(request: SearchRequest):
    """
    Эндпойнт для поиска документов на основе запроса.

    :param request: Объект запроса SearchRequest с полем query.
    :return: Объект ответа SearchResult с результатами поиска.
    """
    try:
        search_items = SearchService.process_search(request.query)
        return SearchResult(results=search_items)
    except Exception:
        logger.exception("Search operation failed.")
        raise HTTPException(status_code=500, detail="Internal Server Error")