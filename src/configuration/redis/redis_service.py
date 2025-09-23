from typing import Annotated, Optional
import redis.asyncio as redis
from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict
from redis.asyncio.connection import BlockingConnectionPool, Retry
from redis.backoff import ExponentialBackoff
from redis.exceptions import ConnectionError, TimeoutError, BusyLoadingError


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_prefix="redis_"
    )

    host: str
    port: int
    database: int
    password: str


class RedisConnectionService:
    def __init__(self):
        self.settings = RedisSettings()
        self._client: Optional[redis.Redis] = None

    async def connect(self) -> redis.Redis:
        """Initialize Redis client with connection pool"""
        if self._client is not None:
            return self._client

        connection_pool = BlockingConnectionPool(
            host=self.settings.host,
            port=self.settings.port,
            db=self.settings.database,
            password=self.settings.password,
            max_connections=100,
            timeout=10,
            retry_on_timeout=True,
            decode_responses=True,
            health_check_interval=30,
            retry=Retry(
                backoff=ExponentialBackoff(base=1, cap=30),
                retries=10,
                supported_errors=(ConnectionError, TimeoutError),
            ),
            retry_on_error=[BusyLoadingError, ConnectionError, TimeoutError],
        )

        self._client = redis.Redis(connection_pool=connection_pool)
        await self._client.ping()
        print("Redis connection established successfully.")
        return self._client

    async def get_client(self) -> redis.Redis:
        """Get Redis client, connect if not already connected"""
        if self._client is None:
            return await self.connect()
        return self._client

    async def disconnect(self):
        """Close the Redis connection"""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            print("Redis connection closed.")


# Singleton instance
redis_connection_service = RedisConnectionService()


# Dependency function
async def get_redis() -> redis.Redis:
    """Dependency to get Redis client"""
    return await redis_connection_service.get_client()


# Type alias for convenience
RedisClient = Annotated[redis.Redis, Depends(get_redis)]
