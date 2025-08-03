import logging
from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database
from texts import get_text
from states import Form
from keyboards import get_channels_menu_keyboard, get_channel_detail_keyboard, get_confirm_remove_keyboard

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
    await callback.message.edit_text(get_text('add_channel_prompt', lang))
    await callback.answer()

@router.message(Form.waiting_for_channel_forward, F.forward_from_chat)
async def process_channel_forward(message: types.Message, state: FSMContext, bot: Bot):
    """Processes the forwarded message to register the channel."""
    user_id = message.from_user.id
    lang = await database.get_user_language(user_id) or 'en'

    try:
        if message.forward_from_chat.type != 'channel':
            await message.answer(get_text('invalid_message_type', lang))
            await state.clear()
            return

        channel_id = message.forward_from_chat.id

        if await database.is_channel_registered(channel_id, user_id):
            await message.answer(get_text('channel_already_exists', lang))
            await state.clear()
            return

        # Check if bot is admin
        bot_member = await bot.get_chat_member(chat_id=channel_id, user_id=bot.id)
        if bot_member.status not in ['administrator', 'creator']:
            await message.answer(get_text('channel_add_error', lang))
            await state.clear()
            return

        # Check if user is admin
        user_member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        if user_member.status not in ['administrator', 'creator']:
            await message.answer(get_text('channel_add_error', lang))
            await state.clear()
            return

        await database.add_channel(channel_id, user_id)
        await message.answer(get_text('channel_added_success', lang))

    except TelegramBadRequest as e:
        logging.error(f"Error checking admin status for channel {channel_id}: {e}")
        await message.answer(get_text('channel_add_error', lang))
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        await message.answer(get_text('error_occurred', lang))
    finally:
        await state.clear()

@router.message(Form.waiting_for_channel_forward)
async def invalid_channel_forward(message: types.Message, state: FSMContext):
    """Handles invalid forwards (not from channel)."""
    lang = await database.get_user_language(message.from_user.id) or 'en'
    await message.answer(get_text('invalid_message_type', lang))
    await state.clear()

@router.callback_query(F.data == "my_channels")
async def list_my_channels(callback: types.CallbackQuery, bot: Bot):
    """Lists all channels registered by the user with clickable buttons."""
    user_id = callback.from_user.id
    lang = await database.get_user_language(user_id) or 'en'
    channels = await database.get_user_channels(user_id)

    if not channels:
        await callback.message.edit_text(get_text('no_channels_registered', lang))
        await callback.answer()
        return

    builder = InlineKeyboardBuilder()
    response_text = f"<b>{get_text('your_channels_list', lang)}</b>\n\n"
    
    for i, channel in enumerate(channels, 1):
        try:
            chat = await bot.get_chat(channel[0])
            response_text += f"{i}. {chat.title}\n"
            builder.row(types.InlineKeyboardButton(
                text=f"📢 {chat.title}", 
                callback_data=f"channel_detail_{channel[0]}"
            ))
        except Exception:
            response_text += f"{i}. Unknown Channel (ID: {channel[0]})\n"
            builder.row(types.InlineKeyboardButton(
                text=f"❓ Unknown Channel", 
                callback_data=f"channel_detail_{channel[0]}"
            ))

    await callback.message.edit_text(response_text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("channel_detail_"))
async def show_channel_detail(callback: types.CallbackQuery, bot: Bot):
    """Shows channel details with remove option."""
    channel_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    lang = await database.get_user_language(user_id) or 'en'

    try:
        chat = await bot.get_chat(channel_id)
        text = f"📢 <b>{chat.title}</b>\n\n"
        text += f"🆔 ID: <code>{channel_id}</code>\n"
        if chat.username:
            text += f"🔗 @{chat.username}\n"
        
        await callback.message.edit_text(
            text, 
            reply_markup=get_channel_detail_keyboard(lang, channel_id),
            parse_mode="HTML"
        )
    except Exception:
        text = f"❓ <b>Unknown Channel</b>\n\n"
        text += f"🆔 ID: <code>{channel_id}</code>\n"
        await callback.message.edit_text(
            text, 
            reply_markup=get_channel_detail_keyboard(lang, channel_id),
            parse_mode="HTML"
        )
    
    await callback.answer()

@router.callback_query(F.data.startswith("remove_channel_"))
async def confirm_remove_channel(callback: types.CallbackQuery, bot: Bot):
    """Asks for confirmation before removing channel."""
    channel_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    lang = await database.get_user_language(user_id) or 'en'

    try:
        chat = await bot.get_chat(channel_id)
        channel_title = chat.title
    except Exception:
        channel_title = f"Unknown Channel (ID: {channel_id})"

    text = get_text('confirm_remove_channel', lang).format(channel_title=channel_title)
    await callback.message.edit_text(
        text, 
        reply_markup=get_confirm_remove_keyboard(lang, channel_id),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("confirm_remove_"))
async def remove_channel(callback: types.CallbackQuery):
    """Removes the channel from user's list."""
    channel_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    lang = await database.get_user_language(user_id) or 'en'

    try:
        await database.remove_channel(channel_id, user_id)
        await callback.message.edit_text(get_text('channel_removed_success', lang))
    except Exception as e:
        logging.error(f"Error removing channel {channel_id} for user {user_id}: {e}")
        await callback.message.edit_text(get_text('error_occurred', lang))
    
    await callback.answer()

@router.callback_query(F.data == "cancel_remove")
async def cancel_remove_channel(callback: types.CallbackQuery):
    """Cancels channel removal."""
    lang = await database.get_user_language(callback.from_user.id) or 'en'
    await callback.message.edit_text(get_text('operation_cancelled', lang))
    await callback.answer()
