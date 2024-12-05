# KONSPECTO/backend/app/services/index_service.py

import logging

from .vector_db import get_index

logger = logging.getLogger("app.services.index_service")


def get_query_engine():
    """
    Lazily initializes and returns the query engine.

    :return: An instance of the query engine.
    """
    index = get_index()
    logger.debug("Obtained VectorStoreIndex from IndexManager.")
    query_engine = index.as_query_engine(similarity_top_k=1)
    logger.debug("Query engine initialized successfully.")
    return query_engine
