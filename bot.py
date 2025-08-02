import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import BOT_TOKEN
from texts import get_text, TEXTS

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# --- Keyboard Markup ---
def get_language_keyboard():
    """Creates an inline keyboard for language selection using texts from the locales file."""
    buttons = [
        [
            InlineKeyboardButton(text=TEXTS['choose_language_button']['fa'], callback_data="lang_fa"),
            InlineKeyboardButton(text=TEXTS['choose_language_button']['en'], callback_data="lang_en")
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


# --- Command Handlers ---
@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` command.
    It uses texts from both languages for the initial prompt.
    """
    welcome_text = (
        f"{get_text('welcome', 'fa')}\n"
        f"{get_text('welcome', 'en')}"
    )
    await message.answer(welcome_text, reply_markup=get_language_keyboard())


# --- Callback Query Handlers ---
@dp.callback_query(F.data == "lang_fa")
async def process_lang_fa(callback_query: types.CallbackQuery):
    """
    Handles the 'Farsi' language selection by using the text getter.
    """
    await callback_query.answer()  # Close the loading state on the button
    # Edit the original message with the Farsi confirmation text
    await callback_query.message.edit_text(get_text('lang_selected', 'fa'))


@dp.callback_query(F.data == "lang_en")
async def process_lang_en(callback_query: types.CallbackQuery):
    """
    Handles the 'English' language selection by using the text getter.
    """
    await callback_query.answer()  # Close the loading state on the button
    # Edit the original message with the English confirmation text
    await callback_query.message.edit_text(get_text('lang_selected', 'en'))


# --- Main Execution ---
async def main():
    """
    Starts the bot polling.
    """
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
