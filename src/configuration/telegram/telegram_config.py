from typing import Annotated

from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi import Depends


class TelegramSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_prefix="telegram_"
    )

    bot_token: str
    base_webhook_url: str
    webhook_path: str = "/telegram/webhook"
    auth_token: str


telegram_settings = TelegramSettings()


TelegramSettings = Annotated[TelegramSettings, Depends(lambda: telegram_settings)]
