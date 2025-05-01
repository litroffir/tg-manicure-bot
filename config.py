from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

TOKEN = "7874319913:AAGJMeykamMTJ_GyP4P-f2S-ypS3XPCqVMU"

bot = Bot(token=TOKEN)

COMMANDS = [
    BotCommand(command="start", description="Главное меню"),
    BotCommand(command="book", description="Запись на маникюр"),
    BotCommand(command="my_bookings", description="Мои записи"),
    BotCommand(command="masters", description="Список мастеров")
]


async def set_commands(bot):
    await bot.set_my_commands(COMMANDS)