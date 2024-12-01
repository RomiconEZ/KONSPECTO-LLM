# KONSPECTO/backend/app/services/vector_db.py

import json
import logging
from pathlib import Path
from urllib.parse import urlparse

import torch
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.ingestion import (
    DocstoreStrategy,
    IngestionCache,
    IngestionPipeline,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.readers.google import GoogleDriveReader
from llama_index.storage.docstore.redis import RedisDocumentStore
from llama_index.storage.kvstore.redis import RedisKVStore as RedisCache
from llama_index.vector_stores.redis import RedisVectorStore
from redisvl.schema import IndexSchema

from ..core.config import get_settings

logger = logging.getLogger("app.services.vector_db")


class SingletonMeta(type):
    """
    Implementation of Singleton pattern with thread-safety.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        from threading import Lock
        lock = Lock()
        with lock:
            if cls not in cls._instances:
                cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class IndexManager(metaclass=SingletonMeta):
    """
    Singleton class to manage VectorStoreIndex.
    """

    def __init__(self):
        self.index = None

    def initialize_index(self):
        """
        Initialize VectorStoreIndex, vector store, and ingestion pipeline.
        """
        try:
            settings = get_settings()
            logger.info("Initializing VectorStoreIndex...")

            # Parse Redis URL
            parsed_redis_url = urlparse(settings.REDIS_URL)
            redis_host = parsed_redis_url.hostname or "localhost"
            redis_port = parsed_redis_url.port or 6379

            # Configure device
            device = (
                torch.device("mps")
                if torch.backends.mps.is_available()
                else torch.device("cuda" if torch.cuda.is_available() else "cpu")
            )
            logger.info(f"Using device: {device}")

            # Setup embedding model
            embed_model = HuggingFaceEmbedding(
                model_name="sentence-transformers/all-MiniLM-L12-v2",
                device=device,
                parallel_process=False,
                embed_batch_size=16
            )
            logger.info("HuggingFaceEmbedding initialized successfully.")

            # LLM settings
            Settings.llm = None
            logger.info("LLM settings configured.")

            # Custom schema for RedisVectorStore
            custom_schema = IndexSchema.from_dict(
                {
                    "index": {"name": "gdrive", "prefix": "doc"},
                    "fields": [
                        {"type": "tag", "name": "id"},
                        {"type": "tag", "name": "doc_id"},
                        {"type": "text", "name": "text"},
                        {
                            "type": "vector",
                            "name": "vector",
                            "attrs": {
                                "dims": 384,
                                "algorithm": "hnsw",
                                "distance_metric": "cosine",
                            },
                        },
                    ],
                }
            )

            # Initialize RedisVectorStore
            vector_store = RedisVectorStore(
                schema=custom_schema,
                redis_url=settings.REDIS_URL,
            )
            logger.info("RedisVectorStore initialized.")

            # Setup ingestion cache
            cache = IngestionCache(
                cache=RedisCache.from_host_and_port(redis_host, redis_port),
                collection="redis_cache",
            )

            # Setup Ingestion Pipeline
            pipeline = IngestionPipeline(
                transformations=[
                    SentenceSplitter(),
                    embed_model,
                ],
                docstore=RedisDocumentStore.from_host_and_port(
                    redis_host, redis_port, namespace="document_store"
                ),
                vector_store=vector_store,
                cache=cache,
                docstore_strategy=DocstoreStrategy.UPSERTS,
            )
            logger.info("Ingestion pipeline configured.")

            # Initialize VectorStoreIndex
            self.index = VectorStoreIndex.from_vector_store(
                pipeline.vector_store, embed_model=embed_model
            )
            logger.info("VectorStoreIndex created from vector store.")

            # Load documents from Google Drive
            service_account_path = Path(settings.GOOGLE_SERVICE_ACCOUNT_KEY_PATH)
            if not service_account_path.exists():
                logger.error(f"Service account key file not found at {service_account_path}")
                raise FileNotFoundError(f"Service account key file not found at {service_account_path}")

            with service_account_path.open('r') as f:
                google_creds_dict = json.load(f)

            loader = GoogleDriveReader(service_account_key=google_creds_dict, folder_id=settings.FOLDER_ID)
            logger.info("GoogleDriveReader initialized.")

            docs = loader.load_data()
            if not docs:
                logger.warning("No documents were loaded from Google Drive.")
            else:
                logger.info(f"Loaded {len(docs)} documents from Google Drive.")

            # Run ingestion pipeline
            nodes = pipeline.run(documents=docs)
            logger.info(f"Ingested {len(nodes)} nodes into VectorStoreIndex.")

            # Check if index exists
            if vector_store.index_exists():
                logger.info("Index 'gdrive' exists after ingestion.")
            else:
                logger.error("Index 'gdrive' does not exist after ingestion.")

        except Exception as e:
            logger.exception("Failed to set up the ingestion pipeline.")
            raise

    def get_index(self) -> VectorStoreIndex:
        """
        Returns the VectorStoreIndex. Initializes it if not already created.
        """
        if self.index is None:
            logger.info("Index not initialized. Initializing now...")
            self.initialize_index()
        else:
            logger.info("Index already initialized. Returning existing index.")
        return self.index


def get_index() -> VectorStoreIndex:
    """
    Retrieves the VectorStoreIndex instance.
    """
    index_manager = IndexManager()
    return index_manager.get_index()