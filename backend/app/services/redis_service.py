# backend/app/services/redis_service.py
from redis.asyncio import Redis
from typing import Optional
import logging

from ..core.config import settings

logger = logging.getLogger("app.services.redis_service")

class RedisService:
    def __init__(self):
        self.redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def connect(self):
        """Connect to Redis."""
        try:
            await self.redis_client.ping()
            logger.info("Connected to Redis successfully.")
        except Exception as e:
            logger.exception("Failed to connect to Redis.")
            raise

    async def set_key(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """Set a key-value pair in Redis."""
        try:
            return await self.redis_client.set(key, value, ex=expire)
        except Exception as e:
            logger.exception(f"Failed to set key '{key}' in Redis.")
            return False

    async def get_key(self, key: str) -> Optional[str]:
        """Get value by key from Redis."""
        try:
            return await self.redis_client.get(key)
        except Exception as e:
            logger.exception(f"Failed to get key '{key}' from Redis.")
            return None

    async def delete_key(self, key: str) -> int:
        """Delete a key from Redis."""
        try:
            return await self.redis_client.delete(key)
        except Exception as e:
            logger.exception(f"Failed to delete key '{key}' from Redis.")
            return 0

    async def exists_key(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            return bool(await self.redis_client.exists(key))
        except Exception as e:
            logger.exception(f"Failed to check existence of key '{key}' in Redis.")
            return False

    async def close(self):
        """Close the Redis connection."""
        try:
            await self.redis_client.close()
            logger.info("Redis connection closed.")
        except Exception as e:
            logger.exception("Failed to close Redis connection.")