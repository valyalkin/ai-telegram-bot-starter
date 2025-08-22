import logging
from typing import Annotated

from aiogram import Bot, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BotCommand
from fastapi import Depends

from src.ai_bot.user.user_service import UserServiceAnnotated, UserService, user_service
from src.configuration.telegram.bot import TelegramBotService, telegram_bot_service

logger = logging.getLogger(__name__)


class LangGraphBotService:
    def __init__(self,
                 telegram_bot_service: TelegramBotService,
                 user_service: UserService
                 ):
        self._telegram_bot_service = telegram_bot_service
        self._bot = telegram_bot_service.get_bot()
        self._router = telegram_bot_service.get_router()
        self._user_service = user_service
        
        self._setup_handlers()

    async def __check_user_registration(self, message: Message) -> bool:
        telegram_id = message.from_user.id
        return await self._user_service.is_user_registered(telegram_id)


    def _setup_handlers(self):
        @self._router.message(CommandStart())
        async def start_command_handler(
                message: Message
        ):
            if not await self.__check_user_registration(message):
                # Register user if not registered
                await message.answer(
                    text="You are not registered, please register first by sending your ID.",
                )
                return

            await message.answer(
                text="Hello! I am your AI bot. How can I assist you today?",
            )
        
        @self._router.message(Command("id"))
        async def cmd_id(message: Message) -> None:
            await message.answer(f"Your ID: {message.from_user.id}")
    
    async def set_bot_commands(self):
        commands = [
            BotCommand(command="/id", description="👋 Get my ID"),
            BotCommand(command="/start", description="🚀 Start the bot"),
        ]
        try:
            await self._bot.set_my_commands(commands)
            logger.info("Bot commands set successfully")
        except Exception as e:
            logger.error(f"Can't set commands - {e}")

langgraph_bot_service = LangGraphBotService(
    telegram_bot_service=telegram_bot_service,
    user_service=user_service
)