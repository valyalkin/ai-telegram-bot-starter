from typing import Annotated

from src.configuration.redis.redis_service import RedisClient
from src.configuration.telegram.telegram_config import TelegramSettings, telegram_settings
from aiogram import Router, Dispatcher, Bot
from aiogram.types import WebhookInfo, BotCommand
from fastapi import Depends
import logging

logger = logging.getLogger(__name__)

class TelegramBotService:

    def __init__(self, telegram_settings: TelegramSettings):
        self._telegram_settings = telegram_settings

        dispatcher = Dispatcher()
        telegram_router = Router(name="telegram")
        dispatcher.include_router(telegram_router)

        self._dispatcher = dispatcher
        self._bot = Bot(token=telegram_settings.bot_token)

    async def set_webhook(self):
        logger.info("Setting up telegram webhook")

        # Check and set webhook for Telegram
        async def check_webhook() -> WebhookInfo | None:
            try:
                webhook_info = await self._bot.get_webhook_info()
                return webhook_info
            except Exception as e:
                logging.error(f"Can't get webhook info - {e}")
                return

        current_webhook_info = await check_webhook()

        try:
            base_url = self._telegram_settings.base_webhook_url
            path = self._telegram_settings.webhook_path
            token = self._telegram_settings.auth_token

            await self._bot.set_webhook(
                url = f"{base_url}{path}",
                secret_token=token,
                drop_pending_updates=current_webhook_info.pending_update_count > 0,
                max_connections=40,
            )
            logging.info(f"Updated bot info: {await check_webhook()}")
        except Exception as e:
            logging.error(f"Can't set webhook - {e}")
            raise RuntimeError("Can't set telegram webhook")

    def get_dispatcher(self) -> Dispatcher:
        return self._dispatcher

    def get_bot(self) -> Bot:
        return self._bot

telegram_bot_service = TelegramBotService(telegram_settings=telegram_settings)

TelegramBot = Annotated[TelegramBotService, Depends(lambda: telegram_bot_service)]





