from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends

from src.ai_bot.langgraph_bot_service import get_langgraph_bot_service
from src.ai_bot.user.user_service import get_user_service
from src.configuration.postgres.postgres_config import postgres_connection_service, get_postgres_connection
from src.configuration.redis.redis_service import redis_connection_service
from src.configuration.telegram.bot import telegram_bot_service


@asynccontextmanager
async def lifespan(
        app: FastAPI
):

    # redis
    await redis_connection_service.connect()

    # postgres
    await postgres_connection_service.initialize_db_connection()

    # telegram webhook
    await telegram_bot_service.set_webhook()
    
    # Initialize LangGraphBotService to register handlers
    user_service = get_user_service(postgres_connection_service)
    langgraph_bot_service = get_langgraph_bot_service(telegram_bot_service, user_service)
    
    # Set bot commands through the langgraph service (which has the handlers)
    await langgraph_bot_service.set_bot_commands()

    yield

    await redis_connection_service.disconnect()
