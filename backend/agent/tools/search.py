import logging

from typing import List

from app.services.index_service import get_query_engine

logger = logging.getLogger("agent.tools.search")


class SearchTool:
    """
    Инструмент для выполнения операций поиска с использованием query_engine.
    """

    @staticmethod
    def search(query: str) -> List[str]:
        """
        Выполняет поиск документов по заданному текстовому запросу и возвращает список текстов из найденных документов.

        :param query: Текстовый запрос для поиска документов.
        :return: Список текстовых результатов поиска.
        """
        logger.debug(f"Agent search received query: {query}")

        query_engine = get_query_engine()
        response = query_engine.query(query)
        logger.info(f"Agent received response from query engine for query: {query}")

        results_text = []
        for node_with_score in response.source_nodes:
            if hasattr(node_with_score, "node"):
                node = node_with_score.node
            else:
                logger.warning("node_with_score does not have 'node' attribute.")
                continue

            text = node.text
            if text:
                results_text.append(text)
            else:
                logger.warning(f"Node '{node.id_}' has no text.")

        logger.info(
            f"Agent search query '{query}' returned {len(results_text)} text results."
        )
        return results_text
