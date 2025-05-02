from aiogram.types import BotCommand
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

COMMANDS = [
    BotCommand(command="start", description="Главное меню"),
    BotCommand(command="book", description="Запись на маникюр"),
    BotCommand(command="my_bookings", description="Мои записи"),
    BotCommand(command="masters", description="Список мастеров")
]


async def set_commands(bot):
    await bot.set_my_commands(COMMANDS)


class Settings(BaseSettings):
    bot_token: SecretStr
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


config = Settings()