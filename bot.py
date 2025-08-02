import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from config import BOT_TOKEN
from texts import get_text
import database
from states import Form

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher with memory storage for FSM
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)


# --- Keyboards ---
def get_language_keyboard() -> InlineKeyboardMarkup:
    """Creates an inline keyboard for language selection."""
    buttons = [
        [
            InlineKeyboardButton(text=get_text('choose_language_button', 'fa'), callback_data="lang_fa"),
            InlineKeyboardButton(text=get_text('choose_language_button', 'en'), callback_data="lang_en")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_main_menu_keyboard(lang: str) -> ReplyKeyboardMarkup:
    """Creates a reply keyboard for the main menu."""
    buttons = [
        [KeyboardButton(text=get_text('set_footer_button', lang))]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


# --- Command Handlers ---
@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    """Handler for the /start command. Prompts for language selection."""
    welcome_text = f"{get_text('welcome', 'fa')}\n{get_text('welcome', 'en')}"
    await message.answer(welcome_text, reply_markup=get_language_keyboard())

@dp.message(Command("menu"))
async def show_menu(message: types.Message):
    """Handler for the /menu command. Shows the main menu."""
    lang = await database.get_user_language(message.from_user.id) or 'en'
    await message.answer(get_text('main_menu', lang), reply_markup=get_main_menu_keyboard(lang))


# --- Callback Query Handlers ---
@dp.callback_query(F.data.startswith("lang_"))
async def process_language_selection(callback_query: types.CallbackQuery):
    """Handles language selection, saves it to DB, and shows the main menu."""
    lang = callback_query.data.split("_")[1]
    user_id = callback_query.from_user.id

    await database.add_or_update_user(user_id, lang)

    await callback_query.answer()
    await callback_query.message.edit_text(get_text('lang_selected', lang))
    await callback_query.message.answer(get_text('main_menu', lang), reply_markup=get_main_menu_keyboard(lang))


# --- Footer Setting Handlers ---
@dp.message(F.text.in_([get_text('set_footer_button', 'fa'), get_text('set_footer_button', 'en')]))
async def prompt_for_footer(message: types.Message, state: FSMContext):
    """Prompts the user to enter their footer text and sets the state."""
    user_id = message.from_user.id
    lang = await database.get_user_language(user_id) or 'en'

    await state.set_state(Form.waiting_for_footer)
    await message.answer(get_text('prompt_for_footer', lang))

@dp.message(Form.waiting_for_footer, F.text)
async def process_footer_text(message: types.Message, state: FSMContext):
    """Receives the footer text, saves it to the DB, and clears the state."""
    user_id = message.from_user.id
    lang = await database.get_user_language(user_id) or 'en'

    await database.set_footer_text(user_id, message.text)
    await state.clear()

    await message.answer(get_text('footer_set_success', lang), reply_markup=get_main_menu_keyboard(lang))


# --- Main Execution ---
async def main():
    """Initializes the database and starts the bot polling."""
    await database.init_db()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
