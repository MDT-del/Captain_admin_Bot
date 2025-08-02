import logging
from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from typing import List, Dict

import database
from texts import get_text
from states import Form
from keyboards import get_post_action_keyboard, get_channel_selection_keyboard, get_caption_choice_keyboard

router = Router()

# --- 1. Content Entry Point ---

@router.message(F.content_type.in_({'text', 'photo', 'video', 'document', 'audio', 'voice'}))
async def content_entry_handler(message: types.Message, state: FSMContext):
    """
    This handler catches any user content, checks if they have channels,
    and shows the initial action menu.
    """
    user_id = message.from_user.id
    lang = await database.get_user_language(user_id) or 'en'

    user_channels = await database.get_user_channels(user_id)
    if not user_channels:
        await message.answer(get_text('error_no_channels_for_broadcast', lang))
        return

    # Store the message to be forwarded
    await state.set_data({
        'post_message_id': message.message_id,
        'post_chat_id': message.chat.id,
        'selected_channels': []
    })

    await message.answer(
        get_text('post_action_menu_title', lang),
        reply_markup=get_post_action_keyboard(lang)
    )


# --- 2. Broadcasting Workflow Handlers ---

@router.callback_query(F.data == "cancel_broadcast")
async def cancel_broadcast_handler(callback: types.CallbackQuery, state: FSMContext):
    """Cancels the entire broadcasting operation."""
    lang = await database.get_user_language(callback.from_user.id) or 'en'
    await state.clear()
    await callback.message.edit_text(get_text('operation_cancelled', lang))
    await callback.answer()

@router.callback_query(F.data == "send_now")
async def send_now_handler(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Starts the channel selection process."""
    user_id = callback.from_user.id
    lang = await database.get_user_language(user_id) or 'en'

    db_channels = await database.get_user_channels(user_id)

    all_channels_info = []
    for channel_tuple in db_channels:
        try:
            chat = await bot.get_chat(channel_tuple[0])
            all_channels_info.append({'id': chat.id, 'title': chat.title})
        except Exception as e:
            logging.warning(f"Could not get info for channel {channel_tuple[0]}: {e}")

    if not all_channels_info:
        await callback.message.edit_text(get_text('error_no_channels_for_broadcast', lang))
        await state.clear()
        await callback.answer()
        return

    await state.update_data(all_channels=all_channels_info)

    await callback.message.edit_text(
        get_text('select_channels_prompt', lang),
        reply_markup=get_channel_selection_keyboard(lang, all_channels_info, [])
    )
    await state.set_state(Form.selecting_channels)
    await callback.answer()


@router.callback_query(Form.selecting_channels, F.data.startswith("select_channel_"))
async def select_channel_handler(callback: types.CallbackQuery, state: FSMContext):
    """Handles toggling channel selection."""
    channel_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    lang = await database.get_user_language(user_id) or 'en'

    data = await state.get_data()
    selected = data.get('selected_channels', [])
    all_channels = data.get('all_channels', [])

    if channel_id in selected:
        selected.remove(channel_id)
    else:
        selected.append(channel_id)

    await state.update_data(selected_channels=selected)

    await callback.message.edit_reply_markup(
        reply_markup=get_channel_selection_keyboard(lang, all_channels, selected)
    )
    await callback.answer()


@router.callback_query(Form.selecting_channels, F.data == "confirm_channels")
async def confirm_channels_handler(callback: types.CallbackQuery, state: FSMContext):
    """Asks the user if they want to add a caption."""
    lang = await database.get_user_language(callback.from_user.id) or 'en'
    await state.set_state(None) # Clear state to move to next step
    await callback.message.edit_text(
        get_text('ask_for_caption_prompt', lang),
        reply_markup=get_caption_choice_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("add_caption_"))
async def caption_choice_handler(callback: types.CallbackQuery, state: FSMContext):
    """Handles the 'Yes' or 'No' for adding a caption."""
    choice = callback.data.split("_")[2]
    lang = await database.get_user_language(callback.from_user.id) or 'en'

    if choice == "yes":
        await state.set_state(Form.waiting_for_caption)
        await callback.message.edit_text(get_text('prompt_for_caption', lang))
    else:
        # If no caption, proceed directly to sending
        await callback.message.edit_text("در حال ارسال...")
        await send_final_post(callback.from_user.id, state, bot)

    await callback.answer()


@router.message(Form.waiting_for_caption, F.text)
async def process_caption_handler(message: types.Message, state: FSMContext, bot: Bot):
    """Receives the caption and triggers the final sending."""
    await state.update_data(caption=message.text)
    await message.answer("کپشن دریافت شد. در حال ارسال...")
    await send_final_post(message.from_user.id, state, bot)


# --- 3. Final Sending Logic ---

async def send_final_post(user_id: int, state: FSMContext, bot: Bot):
    """A helper function to perform the final broadcast."""
    data = await state.get_data()
    lang = await database.get_user_language(user_id) or 'en'

    post_message_id = data['post_message_id']
    post_chat_id = data['post_chat_id']
    target_channels = data['selected_channels']
    caption = data.get('caption')

    footer = await database.get_user_footer(user_id)

    final_caption = ""
    if caption:
        final_caption += caption
    if footer:
        if final_caption:
            final_caption += f"\n\n{footer}"
        else:
            final_caption = footer

    sent_count = 0
    for channel_id in target_channels:
        try:
            await bot.copy_message(
                chat_id=channel_id,
                from_chat_id=post_chat_id,
                message_id=post_message_id,
                caption=final_caption if final_caption else None,
                parse_mode="HTML"
            )
            sent_count += 1
        except Exception as e:
            logging.error(f"Failed to send to channel {channel_id}: {e}")

    await bot.send_message(user_id, get_text('broadcast_success', lang).format(count=sent_count))
    await state.clear()
