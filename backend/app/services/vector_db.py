import logging
import os
from pathlib import Path

import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
import torch

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем URL Chroma из переменных окружения или используем значение по умолчанию
CHROMA_URL = os.getenv("CHROMA_URL", "http://chroma:8000")

# Определяем устройство (MPS, CUDA или CPU)
device = (
    torch.device("mps")
    if torch.backends.mps.is_available()
    else torch.device("cuda" if torch.cuda.is_available() else "cpu")
)
logger.info(f"Using device: {device}")

# Настраиваем модель в Settings
try:
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="intfloat/multilingual-e5-base",
        device=device,
        parallel_process=False,
        embed_batch_size=2
    )
    logger.info("HuggingFaceEmbedding initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize HuggingFaceEmbedding: {e}")
    raise

try:
    Settings.llm = None
    logger.info("LLM initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize LLM: {e}")
    raise

# Путь к документам
current_file = Path(__file__).resolve()
documents_path = current_file.parents[1] / 'documents'

if not documents_path.exists():
    logger.error(f"Documents directory not found at {documents_path}")
    raise FileNotFoundError("Documents directory not found")

try:
    documents = SimpleDirectoryReader(documents_path).load_data()
    logger.info(f"Loaded {len(documents)} documents successfully")
except Exception as e:
    logger.error(f"Failed to load documents: {e}")
    raise

# Инициализация Chroma клиента и создание/получение коллекции
try:
    remote_db = chromadb.HttpClient(host=CHROMA_URL.split("://")[-1].split(":")[0],
                                   port=int(CHROMA_URL.split(":")[-1]))
    chroma_collection = remote_db.get_or_create_collection("quickstart")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    logger.info("Chroma VectorStore initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Chroma client: {e}")
    raise

# Создание индекса из документов с использованием Chroma
try:
    index = VectorStoreIndex.from_documents(
        documents=documents,
        storage_context=storage_context,
        embed_model=Settings.embed_model
    )
    logger.info("VectorStoreIndex initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize VectorStoreIndex: {e}")
    raise

def get_index():
    """
    Функция для получения индекса.
    """
    return index