import json
import logging
import os
from pathlib import Path

import torch
from dotenv import load_dotenv
from redisvl.schema import IndexSchema
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

# Настройка логирования
logger = logging.getLogger(__name__)

class IndexManager:
    """
    Singleton class to manage the VectorStoreIndex.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IndexManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.index = None
        self._initialized = True

    def initialize_index(self):
        """
        Initializes the VectorStoreIndex, vector store, and ingestion pipeline.
        Raises:
            FileNotFoundError: If the configuration directory is not found.
            Exception: If any part of the initialization fails.
        """
        try:
            # Получаем URL Chroma из переменных окружения или используем значение по умолчанию
            CHROMA_URL = os.getenv("CHROMA_URL", "http://chroma:8000")

            # Определяем путь директории конфигурации
            config_path = Path(__file__).parent.parent / 'config'
            if config_path.exists() and config_path.is_dir():
                logger.info(f"Директория конфигурации '{config_path}' существует.")
            else:
                logger.error(f"Директория конфигурации '{config_path}' не найдена.")
                raise FileNotFoundError(f"Директория конфигурации '{config_path}' не найдена.")

            # Пути к файлам
            env_path = config_path / '.env'
            google_creds_path = config_path / 'service_account_key.json'

            # Логгирование найденных путей
            logger.info(f"Путь к .env: {env_path}")
            logger.info(f"Путь к service_account_key.json: {google_creds_path}")

            # Загружаем переменные окружения из локального .env файла, не переопределяя уже существующие
            load_dotenv(dotenv_path=env_path, override=False)

            FOLDER_ID = os.getenv('FOLDER_ID')
            logger.info(f"ID папки на диске: {FOLDER_ID}")

            # Обновляем REDIS_URL для использования имени хоста Redis в Docker Compose
            REDIS_URL = os.getenv("REDIS_URL", "redis://redis-stack:6379")

            # Определяем устройство (MPS, CUDA или CPU)
            device = (
                torch.device("mps")
                if torch.backends.mps.is_available()
                else torch.device("cuda" if torch.cuda.is_available() else "cpu")
            )
            logger.info(f"Using device: {device}")

            # Настраиваем модель в Settings
            embed_model = HuggingFaceEmbedding(
                model_name="sentence-transformers/all-MiniLM-L12-v2",
                device=device,
                parallel_process=False,
                embed_batch_size=16
            )
            logger.info("HuggingFaceEmbedding initialized successfully")

            Settings.llm = None
            logger.info("LLM initialized successfully")

            # Настройка схемы индекса
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

            vector_store = RedisVectorStore(
                schema=custom_schema,
                redis_url=REDIS_URL,
            )

            # Set up the ingestion cache layer
            cache = IngestionCache(
                cache=RedisCache.from_host_and_port("redis-stack", 6379),
                collection="redis_cache",
            )

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

            self.index = VectorStoreIndex.from_vector_store(
                pipeline.vector_store, embed_model=embed_model
            )

            google_creds_json = google_creds_path.read_text().replace('\n', '')
            google_creds_dict = json.loads(google_creds_json)

            loader = GoogleDriveReader(service_account_key=google_creds_dict, folder_id=FOLDER_ID)

            # Load data with additional logging
            try:
                docs = loader.load_data()
                if not docs:
                    logger.warning("No documents were loaded from Google Drive.")
                else:
                    logger.info(f"Loaded {len(docs)} documents from Google Drive.")
                nodes = pipeline.run(documents=docs)
                logger.info(f"Ingested {len(nodes)} Nodes")
            except Exception as e:
                logger.error(f"Failed to load documents: {e}")
                raise

            if vector_store.index_exists():
                logger.info("Index 'gdrive' exists after ingestion.")
            else:
                logger.error("Index 'gdrive' does not exist after ingestion.")

        except Exception as e:
            logger.error(f"Failed to set up the ingestion pipeline: {e}")
            raise

    def get_index(self):
        """
        Returns the VectorStoreIndex. Initializes it if not already done.

        Returns:
            VectorStoreIndex: The initialized index.
        """
        if self.index is None:
            logger.info("Index is not initialized. Initializing now...")
            self.initialize_index()
        else:
            logger.info("Index already initialized. Returning existing index.")
        return self.index


# Singleton instance of IndexManager
_index_manager = IndexManager()


def get_index():
    """
    Retrieves the VectorStoreIndex instance.

    Returns:
        VectorStoreIndex: The initialized index.
    """
    return _index_manager.get_index()