import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
# It's recommended to store your bot token in an environment variable.
# Create a .env file and add the line: BOT_TOKEN='YOUR_TELEGRAM_BOT_TOKEN'
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN found in environment variables. Please set it in your .env file.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Keyboard Markup ---
def get_language_keyboard():
    """Creates an inline keyboard for language selection."""
    buttons = [
        [
            InlineKeyboardButton(text="فارسی 🇮🇷", callback_data="lang_fa"),
            InlineKeyboardButton(text="English 🇬🇧", callback_data="lang_en")
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

# --- Command Handlers ---
@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` command
    """
    welcome_text = (
        "لطفا زبان خود را انتخاب کنید.\n"
        "Please select your language."
    )
    await message.answer(welcome_text, reply_markup=get_language_keyboard())

# --- Callback Query Handlers ---
@dp.callback_query(F.data == "lang_fa")
async def process_lang_fa(callback_query: types.CallbackQuery):
    """
    Handles the 'Farsi' language selection.
    """
    await callback_query.answer() # Close the loading state on the button
    await callback_query.message.edit_text("شما زبان فارسی را انتخاب کردید. خوش آمدید!")


@dp.callback_query(F.data == "lang_en")
async def process_lang_en(callback_query: types.CallbackQuery):
    """
    Handles the 'English' language selection.
    """
    await callback_query.answer() # Close the loading state on the button
    await callback_query.message.edit_text("You have selected English. Welcome!")


# --- Main Execution ---
async def main():
    """
    Starts the bot polling.
    """
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
