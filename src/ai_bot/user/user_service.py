from typing import Annotated
from fastapi import Depends
from src.api.model.user import BotUser
from src.configuration.postgres.postgres_config import PostgresConnectionService, get_postgres_connection


class UserService:
    def __init__(self, db: PostgresConnectionService):
        self._db: PostgresConnectionService = db

    async def register_user(self, user: BotUser):

        pool = self._db.get_connection()
        async with pool.acquire() as conn:

            await conn.execute(
                '''
                CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL
                )
                '''
            )

            await conn.execute(
                '''
                INSERT INTO users (telegram_id) VALUES ($1)
                ON CONFLICT (telegram_id) DO NOTHING
                 ''',
                user.telegram_id
            )

    async def is_user_registered(self, telegram_id: int) -> bool:
        pool = self._db.get_connection()
        async with pool.acquire() as conn:
            result = await conn.fetchrow(
                'SELECT * FROM users WHERE telegram_id = $1',
                telegram_id
            )
            return result is not None


def get_user_service(db: Annotated[PostgresConnectionService, Depends(get_postgres_connection)]) -> UserService:
    return UserService(db)


UserServiceAnnotated = Annotated[UserService, Depends(get_user_service)]