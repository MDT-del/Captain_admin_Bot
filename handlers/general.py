from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command

import database
from texts import get_text
from keyboards import get_language_keyboard, get_main_menu_keyboard

# All handlers for this module are registered on a separate router
router = Router()


@router.message(CommandStart())
async def send_welcome(message: types.Message):
    """Handler for the /start command. Prompts for language selection."""
    await message.answer(
        f"{get_text('welcome', 'fa')}\n{get_text('welcome', 'en')}",
        reply_markup=get_language_keyboard()
    )

@router.message(Command("menu"))
async def show_menu(message: types.Message):
    """Handler for the /menu command. Shows the main menu."""
    lang = await database.get_user_language(message.from_user.id) or 'en'
    await message.answer(get_text('main_menu', lang), reply_markup=get_main_menu_keyboard(lang))

@router.callback_query(F.data.startswith("lang_"))
async def process_language_selection(callback: types.CallbackQuery):
    """Handles language selection, saves it to DB, and shows the main menu."""
    lang = callback.data.split("_")[1]
    user_id = callback.from_user.id

    await database.add_or_update_user(user_id, lang)

    await callback.answer()
    await callback.message.edit_text(get_text('lang_selected', lang))
    await callback.message.answer(get_text('main_menu', lang), reply_markup=get_main_menu_keyboard(lang))
