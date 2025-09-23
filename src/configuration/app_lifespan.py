from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.ai_bot.langgraph_bot_service import langgraph_bot_service
from src.ai_bot.user.user_service import user_service
from src.configuration.postgres.postgres_config import postgres_connection_service
from src.configuration.redis.redis_service import redis_connection_service
from src.configuration.telegram.bot import telegram_bot_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # redis
    await redis_connection_service.connect()

    # postgres
    await postgres_connection_service.initialize_db_connection()

    # telegram
    await telegram_bot_service.set_webhook()
    await langgraph_bot_service.set_bot_commands()

    # users
    await user_service.create_users_table()

    yield

    await redis_connection_service.disconnect()
    await postgres_connection_service.close_db_connection()
