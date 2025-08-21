from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends
from src.configuration.redis.redis_service import redis_connection_service
from src.configuration.telegram.bot import telegram_bot_service


@asynccontextmanager
async def lifespan(
        app: FastAPI
):

    # redis
    await redis_connection_service.connect()

    # telegram webhook
    await telegram_bot_service.set_webhook()

    yield

    await redis_connection_service.disconnect()
