"""Redis client for IES backend.

Provides async Redis client for session state persistence and caching.
"""

import redis.asyncio as redis
from typing import Optional

from ..config import settings


class RedisClient:
    """Async Redis client singleton.

    Uses connection pooling for efficient resource usage.
    """

    _instance: Optional["RedisClient"] = None
    _client: Optional[redis.Redis] = None

    def __new__(cls) -> "RedisClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def get_client(self) -> redis.Redis:
        """Get or create Redis client connection.

        Returns:
            Async Redis client
        """
        if self._client is None:
            self._client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._client

    async def close(self) -> None:
        """Close Redis connection."""
        if self._client is not None:
            await self._client.close()
            self._client = None

    async def ping(self) -> bool:
        """Check Redis connection health.

        Returns:
            True if Redis is reachable, False otherwise
        """
        try:
            client = await self.get_client()
            await client.ping()
            return True
        except Exception:
            return False


# Module-level singleton
redis_client = RedisClient()
