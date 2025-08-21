import logging
from typing import Annotated

from fastapi import APIRouter, Request, Header
from aiogram import types
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