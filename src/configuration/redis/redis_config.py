from typing import Optional

import redis.asyncio as redis
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


redis_settings = RedisSettings()


class AsyncRedisConnection:
    def __init__(self):
        self._redis_client: Optional[redis.Redis] = None

    async def create_connection(self) -> redis.Redis:
        """
        Initialize Redis client with connection pool.
        :return:
        """

        if self._redis_client is not None:
            return self._redis_client

        connection_pool = BlockingConnectionPool(
            host=redis_settings.host,
            port=redis_settings.port,
            db=redis_settings.database,
            password=redis_settings.password,
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

        self._redis_client = redis.Redis(
            connection_pool=connection_pool,
        )

        await self._redis_client.ping()
        print("Redis connection established successfully.")
        return self._redis_client

    async def get_redis_client(self) -> redis.Redis:
        if self._redis_client is None:
            raise RuntimeError("Redis client is not initialized")
        else:
            return self._redis_client

    async def close_connection(self):
        """
        Close the Redis connection.
        :return:
        """
        if self._redis_client is not None:
            await self._redis_client.aclose()
            self._redis_client = None
        else:
            raise RuntimeError("Redis client is not initialized.")


redis_connection = AsyncRedisConnection()
