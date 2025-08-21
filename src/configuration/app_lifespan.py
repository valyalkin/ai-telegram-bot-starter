from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.configuration.redis.redis_service import redis_connection_service


@asynccontextmanager
async def lifespan(app: FastAPI):

    # redis
    await redis_connection_service.connect()

    yield

    await redis_connection_service.disconnect()
