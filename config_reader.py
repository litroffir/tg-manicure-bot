from aiogram.types import BotCommand
from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

COMMANDS = [
    BotCommand(command="start", description="Главное меню"),
    BotCommand(command="book", description="Запись на маникюр"),
    BotCommand(command="my_bookings", description="Мои записи"),
    BotCommand(command="masters", description="Список мастеров")
]


async def set_commands(bot):
    await bot.set_my_commands(COMMANDS)


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class TGConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="BOT_")

    token: SecretStr
    admin_id: int


class DBConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="POSTGRES_")

    host: SecretStr
    port: SecretStr
    db: SecretStr
    user: SecretStr
    password: SecretStr


class Config(BaseSettings):
    telegram: TGConfig = Field(default_factory=TGConfig)
    db: DBConfig = Field(default_factory=DBConfig)

    @classmethod
    def load(cls) -> "Config":
        return cls()


config = Config()