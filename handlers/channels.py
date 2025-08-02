import logging
from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

import database
from texts import get_text
from states import Form
from keyboards import get_channels_menu_keyboard

# All handlers for this module are registered on a separate router
router = Router()


@router.message(F.text.in_([get_text('manage_channels_button', 'fa'), get_text('manage_channels_button', 'en')]))
async def show_channels_menu(message: types.Message):
    """Shows the channel management inline menu."""
    lang = await database.get_user_language(message.from_user.id) or 'en'
    await message.answer(get_text('channels_menu_title', lang), reply_markup=get_channels_menu_keyboard(lang))

@router.callback_query(F.data == "add_channel")
async def prompt_for_channel_forward(callback: types.CallbackQuery, state: FSMContext):
    """Prompts the user to forward a message to register a channel."""
    lang = await database.get_user_language(callback.from_user.id) or 'en'
    await state.set_state(Form.waiting_for_channel_forward)
    await callback.message.edit_text(get_text('prompt_forward_message', lang))
    await callback.answer()

@router.message(Form.waiting_for_channel_forward, F.forward_from_chat)
async def process_channel_forward(message: types.Message, state: FSMContext, bot: Bot):
    """Processes the forwarded message to register the channel."""
    user_id = message.from_user.id
    lang = await database.get_user_language(user_id) or 'en'

    if message.forward_from_chat.type != 'channel':
        # Optional: handle cases where forward is not from a channel
        await state.clear()
        # You might want to add a specific error message for this in texts.py
        await message.answer("Please forward a message from a channel.")
        return

    channel_id = message.forward_from_chat.id

    if await database.is_channel_registered(channel_id, user_id):
        await message.answer(get_text('channel_already_registered', lang))
        await state.clear()
        return

    try:
        bot_member = await bot.get_chat_member(chat_id=channel_id, user_id=bot.id)
        if bot_member.status not in ['administrator', 'creator']:
            await message.answer(get_text('error_bot_not_admin', lang))
            await state.clear()
            return

        user_member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        if user_member.status not in ['administrator', 'creator']:
            await message.answer(get_text('error_not_admin_in_channel', lang))
            await state.clear()
            return

        await database.add_channel(channel_id, user_id)
        await message.answer(get_text('channel_add_success', lang))

    except TelegramBadRequest as e:
        logging.error(f"Error checking admin status for channel {channel_id}: {e}")
        await message.answer(get_text('error_generic', lang))
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        await message.answer(get_text('error_generic', lang))
    finally:
        await state.clear()

@router.callback_query(F.data == "my_channels")
async def list_my_channels(callback: types.CallbackQuery, bot: Bot):
    """Lists all channels registered by the user."""
    user_id = callback.from_user.id
    lang = await database.get_user_language(user_id) or 'en'
    channels = await database.get_user_channels(user_id)

    if not channels:
        await callback.message.edit_text(get_text('no_channels_found', lang))
    else:
        response_text = f"<b>{get_text('your_channels_list', lang)}</b>\n\n"
        for channel in channels:
            try:
                chat = await bot.get_chat(channel[0])
                response_text += f"- {chat.title} (<code>{chat.id}</code>)\n"
            except Exception:
                response_text += f"- Unknown Channel (<code>{channel[0]}</code>)\n"
        await callback.message.edit_text(response_text, parse_mode="HTML")

    await callback.answer()
