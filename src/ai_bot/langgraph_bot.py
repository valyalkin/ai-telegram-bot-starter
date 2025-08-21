import logging

from src.configuration.telegram.bot import telegram_bot_service
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ForceReply
from aiogram.types import WebhookInfo, BotCommand
from aiogram.filters import CommandStart, Command

router = telegram_bot_service.get_router()
bot = telegram_bot_service.get_bot()

async def set_bot_commands():
    # Register commands for Telegram bot (menu)
    commands = [
        BotCommand(command="/id", description="👋 Get my ID"),
        BotCommand(command="/start", description="🚀 Start the bot"),
    ]
    try:
        await bot.set_my_commands(commands)
    except Exception as e:
        logging.error(f"Can't set commands - {e}")

@router.message(CommandStart())
async def start_command_handler(message: Message):
    await message.answer(
        text="Hello! I am your AI bot. How can I assist you today?",
    )

@router.message(Command("id"))
async def cmd_id(message: Message) -> None:
    await message.answer(f"Your ID: {message.from_user.id}")



