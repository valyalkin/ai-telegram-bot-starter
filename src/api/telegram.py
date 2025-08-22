import logging
from typing import Annotated

import asyncpg
from fastapi import APIRouter, Request, Header, Depends
from aiogram import types

from src.ai_bot.user.user_service import UserService, UserServiceAnnotated
from src.api.model.user import BotUser
from src.configuration.postgres.postgres_config import postgres_settings
from src.configuration.telegram.bot import TelegramBotService, TelegramBot

from src.configuration.telegram.telegram_config import telegram_settings

router = APIRouter()


@router.post(telegram_settings.webhook_path)
async def bot_webhook(update: dict,
                      telegram_bot_service: TelegramBot,
                      x_telegram_bot_api_secret_token: Annotated[str | None, Header()] = None,
                      ) -> None | dict:
    """ Register webhook endpoint for telegram bot"""
    if x_telegram_bot_api_secret_token != telegram_settings.auth_token:
        logging.error("Wrong secret token !")
        return {"status": "error", "message": "Wrong secret token !"}
    telegram_update = types.Update(**update)
    dispatcher = telegram_bot_service.get_dispatcher()
    bot = telegram_bot_service.get_bot()
    await dispatcher.feed_update(bot=bot, update=telegram_update)

@router.post("/user/register")
async def register_user(
    user: BotUser,
    user_service: UserServiceAnnotated,
):
    """
    Register a new user in the bot.
    This endpoint is used to register a new user in the bot.
    """
    await user_service.register_user(user)
    # Here you would typically save the user to a database or perform some action
    # For now, we will just log the user information
    logging.info(f"Registering user: {user}")
