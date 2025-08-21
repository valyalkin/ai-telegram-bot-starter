from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.configuration.redis.redis_config import redis_connection


@asynccontextmanager
async def lifespan(app: FastAPI):

    # redis

    await redis_connection.create_connection()
    app.state.redis_connection = redis_connection

    yield

    await redis_connection.close_connection()
