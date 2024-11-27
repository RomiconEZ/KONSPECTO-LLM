# KONSPECTO/backend/app/services/vector_db.py

import json
import logging
from pathlib import Path

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

from ..core.config import settings

logger = logging.getLogger("app.services.vector_db")


class SingletonMeta(type):
    """
    Реализация паттерна Singleton с потокобезопасностью.
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
    Singleton класс для управления VectorStoreIndex.
    """

    def __init__(self):
        self.index = None

    def initialize_index(self):
        """
        Инициализация VectorStoreIndex, vector store и ingestion pipeline.
        """
        try:
            logger.info("Initializing VectorStoreIndex...")

            # Конфигурация устройства
            device = (
                torch.device("mps")
                if torch.backends.mps.is_available()
                else torch.device("cuda" if torch.cuda.is_available() else "cpu")
            )
            logger.info(f"Using device: {device}")

            # Настройка модели эмбеддингов
            embed_model = HuggingFaceEmbedding(
                model_name="sentence-transformers/all-MiniLM-L12-v2",
                device=device,
                parallel_process=False,
                embed_batch_size=16
            )
            logger.info("HuggingFaceEmbedding initialized successfully.")

            # Настройки LLM
            Settings.llm = None
            logger.info("LLM settings configured.")

            # Пользовательская схема для RedisVectorStore
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

            # Инициализация RedisVectorStore
            vector_store = RedisVectorStore(
                schema=custom_schema,
                redis_url=settings.REDIS_URL,
            )
            logger.info("RedisVectorStore initialized.")

            # Настройка кеша для ingestion
            cache = IngestionCache(
                cache=RedisCache.from_host_and_port("redis-stack", 6379),
                collection="redis_cache",
            )

            # Настройка Ingestion Pipeline
            pipeline = IngestionPipeline(
                transformations=[
                    SentenceSplitter(),
                    embed_model,
                ],
                docstore=RedisDocumentStore.from_host_and_port(
                    "redis-stack", 6379, namespace="document_store"
                ),
                vector_store=vector_store,
                cache=cache,
                docstore_strategy=DocstoreStrategy.UPSERTS,
            )
            logger.info("Ingestion pipeline configured.")

            # Инициализация VectorStoreIndex
            self.index = VectorStoreIndex.from_vector_store(
                pipeline.vector_store, embed_model=embed_model
            )
            logger.info("VectorStoreIndex created from vector store.")

            # Загрузка документов из Google Drive
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

            # Запуск ingestion pipeline
            nodes = pipeline.run(documents=docs)
            logger.info(f"Ingested {len(nodes)} nodes into VectorStoreIndex.")

            # Проверка существования индекса
            if vector_store.index_exists():
                logger.info("Index 'gdrive' exists after ingestion.")
            else:
                logger.error("Index 'gdrive' does not exist after ingestion.")

        except Exception as e:
            logger.exception("Failed to set up the ingestion pipeline.")
            raise

    def get_index(self) -> VectorStoreIndex:
        """
        Возвращает VectorStoreIndex. Инициализирует его, если он еще не создан.

        :return: Экземпляр VectorStoreIndex.
        """
        if self.index is None:
            logger.info("Index not initialized. Initializing now...")
            self.initialize_index()
        else:
            logger.info("Index already initialized. Returning existing index.")
        return self.index


def get_index() -> VectorStoreIndex:
    """
    Получает экземпляр VectorStoreIndex.

    :return: Экземпляр VectorStoreIndex.
    """
    index_manager = IndexManager()
    return index_manager.get_index()