from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

import database
from texts import get_text
from states import Form
from keyboards import get_main_menu_keyboard, get_developer_menu_keyboard
from config import DEVELOPER_ID

# All handlers for this module are registered on a separate router
router = Router()


@router.message(F.text.in_([get_text('set_footer_button', 'fa'), get_text('set_footer_button', 'en')]))
async def prompt_for_footer(message: types.Message, state: FSMContext):
    """Prompts the user to enter their footer text and sets the state."""
    lang = await database.get_user_language(message.from_user.id) or 'en'

    await state.set_state(Form.waiting_for_footer)
    await message.answer(get_text('prompt_for_footer', lang))

@router.message(Form.waiting_for_footer, F.text)
async def process_footer_text(message: types.Message, state: FSMContext):
    """Receives the footer text, saves it to the DB, and clears the state."""
    import logging
    current_state = await state.get_state()
    logging.info(f"Footer handler called for user {message.from_user.id}, state: {current_state}, text: {message.text}")
    user_id = message.from_user.id
    lang = await database.get_user_language(user_id) or 'en'

    await database.set_footer_text(user_id, message.text)
    await state.clear()

    # Show appropriate menu based on user type
    if user_id == DEVELOPER_ID:
        await message.answer(get_text('footer_set_success', lang), reply_markup=get_developer_menu_keyboard(lang))
    else:
        await message.answer(get_text('footer_set_success', lang), reply_markup=get_main_menu_keyboard(lang))
