import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import BOT_TOKEN
import database
from handlers import general, footer, channels, broadcasting, premium
from utils.scheduler import send_scheduled_post

# Configure logging
logging.basicConfig(level=logging.INFO)


async def main():
    """
    The main function which initializes the bot, dispatcher, scheduler, routers, and starts polling.
    """
    # Initialize bot, storage and dispatcher
    storage = MemoryStorage()
    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")

    # Initialize the scheduler
    scheduler = AsyncIOScheduler(timezone="Asia/Tehran")

    # Pass scheduler to the dispatcher so it's available in handlers
    dp = Dispatcher(storage=storage, scheduler=scheduler)

    # Include routers from handler modules
    dp.include_router(general.router)
    dp.include_router(footer.router)
    dp.include_router(channels.router)
    dp.include_router(premium.router)
    dp.include_router(broadcasting.router)

    # Initialize the database
    await database.init_db()

    # Start the scheduler
    scheduler.start()

    # Start polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
