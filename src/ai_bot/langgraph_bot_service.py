import asyncio
import logging
import uuid
from typing import Annotated

from aiogram import Bot, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BotCommand
from aiogram.enums import ChatAction
from fastapi import Depends

from src.ai_bot.agent import agent
from src.ai_bot.user.user_service import UserService, user_service
from src.configuration.redis.redis_service import RedisConnectionService, redis_connection_service
from src.configuration.telegram.bot import TelegramBotService, telegram_bot_service
from langgraph.graph.state import CompiledStateGraph
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class LangGraphBotService:
    def __init__(self,
                 telegram_bot_service: TelegramBotService,
                 user_service: UserService,
                 agent: CompiledStateGraph,
                 redis_service: RedisConnectionService
                 ):
        self._telegram_bot_service = telegram_bot_service
        self._bot = telegram_bot_service.get_bot()
        self._router = telegram_bot_service.get_router()
        self._user_service = user_service
        self._agent = agent
        self._redis = redis_service

        self._setup_handlers()

    async def __check_user_registration(self, message: Message) -> bool:
        telegram_id = message.from_user.id
        return await self._user_service.is_user_registered(telegram_id)

    async def __get_session_key_for_user(self, user_id: int) -> str:
        # Get session key or set session key for 5 minutes
        key_name = f"session:{user_id}"
        client: redis.Redis = await self._redis.get_client()

        session_key = await client.get(key_name)

        if not session_key:
            print(f"Setting new session key for user {user_id}")
            session_key = str(uuid.uuid4())
            await client.set(
                name=key_name,
                value=session_key,
                ex=60 * 5
            )

        print(f"Session key: {session_key}")
        return session_key



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

        @self._router.message()
        async def message_handler(message: Message):
            if not await self.__check_user_registration(message):
                # Register user if not registered
                await message.answer(
                    text="You are not registered, please register first by sending your ID.",
                )
                return

            session_key = await self.__get_session_key_for_user(message.from_user.id)

            agent_input = {"messages": [{"role": "user", "content": message.text}]}

            await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

            answer = await self._agent.ainvoke(
                input=agent_input,
                config={"configurable": {"thread_id": str(session_key)}}
            )


            await message.answer(
                text=answer["messages"][-1].content,
            )
    
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
    user_service=user_service,
    agent=agent,
    redis_service=redis_connection_service
)