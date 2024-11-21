# backend/app/api/v1/endpoints/search.py
from fastapi import APIRouter, HTTPException
import logging
from datetime import datetime

from ....services.index_service import query_engine
from ....models.search import SearchRequest, SearchResult, SearchItem

router = APIRouter()
logger = logging.getLogger("app.api.v1.endpoints.search")

@router.post("/", response_model=SearchResult)
async def search_documents(request: SearchRequest):
    """
    Endpoint to search documents based on a query.
    """
    try:
        logger.debug(f"Received search query: {request.query}")
        response = query_engine.query(request.query)
        logger.info("Received response from query engine.")

        # Логирование полной структуры ответа для диагностики
        logger.debug(f"Response structure: {response}")

        search_items = []
        for node_with_score in response.source_nodes:
            # Проверяем, есть ли атрибуты 'node' и 'score' у node_with_score
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

            # Validate necessary metadata fields
            if not all([modified_at_str, file_name, file_id]):
                logger.warning(f"Incomplete metadata for node ID: {node.id_}")
                continue

            try:
                modified_at = datetime.fromisoformat(modified_at_str.replace('Z', '+00:00'))
            except ValueError as ve:
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

        logger.info(f"Search query '{request.query}' returned {len(search_items)} results.")
        return SearchResult(results=search_items)

    except Exception as e:
        logger.exception("Search operation failed.")
        raise HTTPException(status_code=500, detail="Internal Server Error")