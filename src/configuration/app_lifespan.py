from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends

from src.ai_bot.langgraph_bot_service import get_langgraph_bot_service
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

    # telegram bot - initialize service and set commands
    langgraph_bot_service = get_langgraph_bot_service(telegram_bot_service)
    await langgraph_bot_service.set_bot_commands()


    yield

    await redis_connection_service.disconnect()
