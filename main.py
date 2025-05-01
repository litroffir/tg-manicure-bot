from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import set_commands
from handlers import start_router, book_router, back_router, book_management_router
from config import bot
from utils.middleware import MessageUpdaterMiddleware
from utils.storage import BotHolder

import logging
import asyncio

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def on_startup():
    await set_commands(bot)


async def main():
    BotHolder.set_bot(bot)

    dp = Dispatcher(storage=MemoryStorage())

    # dp.update.middleware(MessageUpdaterMiddleware())
    dp.include_router(start_router)
    dp.include_router(book_management_router)
    dp.include_router(book_router)
    dp.include_router(back_router)
    dp.startup.register(on_startup)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
