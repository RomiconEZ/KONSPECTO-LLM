# backend/app/services/redis_service.py
from redis.asyncio import Redis
from typing import Optional


class RedisService:
    def __init__(self, host: str = "redis", port: int = 6379, db: int = 0):
        self.redis_client = Redis(host=host, port=port, db=db, decode_responses=True)

    async def connect(self):
        """Connect to Redis"""
        # Проверка соединения с Redis
        await self.redis_client.ping()

    async def set_key(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """Set a key-value pair in Redis"""
        return await self.redis_client.set(key, value, ex=expire)

    async def get_key(self, key: str) -> Optional[str]:
        """Get value by key from Redis"""
        return await self.redis_client.get(key)

    async def delete_key(self, key: str) -> int:
        """Delete a key from Redis"""
        return await self.redis_client.delete(key)

    async def exists_key(self, key: str) -> bool:
        """Check if key exists in Redis"""
        return bool(await self.redis_client.exists(key))

    async def close(self):
        """Close the Redis connection"""
        await self.redis_client.close()