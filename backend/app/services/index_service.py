# backend/app/services/index_service.py
from .vector_db import get_index
import logging

logger = logging.getLogger("app.services.index_service")

# Initialize the query engine at startup
index = get_index()
query_engine = index.as_query_engine(similarity_top_k=1)

logger.info("Query engine initialized successfully.")
