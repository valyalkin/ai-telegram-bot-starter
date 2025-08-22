from pydantic import BaseModel


class BotUser(BaseModel):
    telegram_id: int