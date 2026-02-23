import logging
from typing import Optional

from redis.asyncio import Redis

from ..core.config import get_settings

logger = logging.getLogger("app.services.redis_service")


class RedisService:
    def __init__(self):
        settings = get_settings()
        self.redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=False)

    async def connect(self):
        """Connect to Redis."""
        await self.redis_client.ping()
        logger.info("Connected to Redis successfully.")

    async def set_key(self, key: str, value: bytes, expire: Optional[int] = None) -> bool:
        """Set a key-value pair in Redis."""
        result = await self.redis_client.set(key, value, ex=expire)
        logger.debug(f"Set key '{key}' in Redis, result: {result}")
        return result

    async def get_key(self, key: str) -> Optional[bytes]:
        """Get value by key from Redis."""
        value = await self.redis_client.get(key)
        logger.debug(f"Get key '{key}' from Redis, found: {value is not None}")
        return value

    async def delete_key(self, key: str) -> int:
        """Delete a key from Redis."""
        result = await self.redis_client.delete(key)
        logger.debug(f"Delete key '{key}' from Redis, result: {result}")
        return result

    async def exists_key(self, key: str) -> bool:
        """Check if key exists in Redis."""
        result = bool(await self.redis_client.exists(key))
        logger.debug(f"Exists key '{key}' in Redis: {result}")
        return result

    async def set_file(self, key: str, data: bytes, expire: Optional[int] = None) -> bool:
        """Save a file to Redis."""
        return await self.set_key(key, data, expire)

    async def get_file(self, key: str) -> Optional[bytes]:
        """Retrieve a file from Redis."""
        return await self.get_key(key)

    async def close(self):
        """Close the Redis connection."""
        try:
            await self.redis_client.close()
            logger.info("Redis connection closed.")
        except Exception:
            logger.exception("Failed to close Redis connection.")