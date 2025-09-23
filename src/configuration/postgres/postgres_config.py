from typing import Optional
import asyncpg
from asyncpg import Pool
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_prefix="postgres_"
    )

    connection_string: str


postgres_settings = PostgresSettings()


class PostgresConnectionService:
    def __init__(self):
        self._settings = postgres_settings
        self._pool: Optional[Pool] = None

    async def initialize_db_connection(self):
        if self._pool is not None:
            print("PostgreSQL connection already initialized.")
            return
        self._pool = await asyncpg.create_pool(
            dsn=self._settings.connection_string,
        )
        print("PostgreSQL connection initialized successfully.")

    async def close_db_connection(self):
        if self._pool:
            await self._pool.close()
            self._pool = None
            print("PostgreSQL connection closed successfully.")

    def get_connection(self) -> Pool:
        return self._pool


postgres_connection_service = PostgresConnectionService()
