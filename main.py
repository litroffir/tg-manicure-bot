from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from config_reader import set_commands, config
from handlers import start_router, book_router, book_management_router, master_router
from back_handlers import back_router
from utils.storage import BotHolder

import logging
import asyncio

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

bot = Bot(token=config.telegram.token.get_secret_value())


async def on_startup():
    await set_commands(bot)


async def main():
    BotHolder.set_bot(bot)

    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start_router)
    dp.include_router(book_management_router)
    dp.include_router(master_router)
    dp.include_router(book_router)
    dp.include_router(back_router)
    dp.startup.register(on_startup)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())