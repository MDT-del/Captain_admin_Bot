import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
import database
from handlers import general, footer, channels, broadcasting

# Configure logging
logging.basicConfig(level=logging.INFO)


async def main():
    """
    The main function which initializes the bot, dispatcher, routers, and starts polling.
    """
    # Initialize bot, storage and dispatcher
    storage = MemoryStorage()
    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher(storage=storage)

    # Include routers from handler modules
    dp.include_router(general.router)
    dp.include_router(footer.router)
    dp.include_router(channels.router)
    dp.include_router(broadcasting.router)

    # Initialize the database
    await database.init_db()

    # Start polling
    # Before starting, we drop pending updates to not process updates that were sent when the bot was offline.
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
