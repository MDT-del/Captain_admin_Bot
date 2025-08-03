from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from typing import List, Dict

from texts import get_text

# --- General Keyboards ---

def get_language_keyboard() -> InlineKeyboardBuilder:
    """Creates an inline keyboard for language selection."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=get_text('choose_language_button', 'fa'), callback_data="lang_fa"),
        InlineKeyboardButton(text=get_text('choose_language_button', 'en'), callback_data="lang_en")
    )
    return builder.as_markup()

def get_main_menu_keyboard(lang: str) -> ReplyKeyboardMarkup:
    """Creates a reply keyboard for the main menu."""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text=get_text('set_footer_button', lang)),
        KeyboardButton(text=get_text('manage_channels_button', lang))
    )
    builder.row(KeyboardButton(text=get_text('upgrade_premium_button', lang)))
    return builder.as_markup(resize_keyboard=True)

def get_developer_menu_keyboard(lang: str) -> ReplyKeyboardMarkup:
    """Creates a reply keyboard for the developer menu."""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text=get_text('developer_stats_button', lang)),
        KeyboardButton(text=get_text('developer_manage_users_button', lang))
    )
    builder.row(KeyboardButton(text=get_text('developer_premium_management_button', lang)))
    builder.row(
        KeyboardButton(text=get_text('set_footer_button', lang)),
        KeyboardButton(text=get_text('manage_channels_button', lang))
    )
    return builder.as_markup(resize_keyboard=True)

# --- Channel Management Keyboards ---

def get_channels_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Creates an inline keyboard for the channel management menu."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=get_text('add_channel_button', lang), callback_data="add_channel"))
    builder.row(InlineKeyboardButton(text=get_text('my_channels_button', lang), callback_data="my_channels"))
    return builder.as_markup()

# --- Broadcasting Keyboards ---

def get_post_action_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Keyboard for initial post action: Send Now, Scheduled, Cancel."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=get_text('send_now_button', lang), callback_data="send_now"),
        InlineKeyboardButton(text=get_text('send_scheduled_button', lang), callback_data="send_scheduled")
    )
    builder.row(InlineKeyboardButton(text=get_text('cancel_broadcast_button', lang), callback_data="cancel_broadcast"))
    return builder.as_markup()

def get_channel_selection_keyboard(lang: str, all_channels: List[Dict], selected_channels: List[int]) -> InlineKeyboardMarkup:
    """Dynamic keyboard for selecting channels. Selected channels are marked."""
    builder = InlineKeyboardBuilder()
    for channel in all_channels:
        channel_id = channel['id']
        channel_title = channel['title']
        text = f"✅ {channel_title}" if channel_id in selected_channels else channel_title
        builder.row(InlineKeyboardButton(text=text, callback_data=f"select_channel_{channel_id}"))

    if selected_channels:
        builder.row(InlineKeyboardButton(text=get_text('confirm_channels_button', lang), callback_data="confirm_channels"))

    return builder.as_markup()

def get_caption_choice_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Keyboard to ask the user if they want to add a caption."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=get_text('add_caption_yes_button', lang), callback_data="add_caption_yes")
    )
    builder.row(
        InlineKeyboardButton(text=get_text('add_caption_no_button', lang), callback_data="add_caption_no")
    )
    return builder.as_markup()

def get_channel_detail_keyboard(lang: str, channel_id: int) -> InlineKeyboardMarkup:
    """Keyboard for channel details with remove option."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=get_text('remove_channel_button', lang), 
                                   callback_data=f"remove_channel_{channel_id}"))
    return builder.as_markup()

def get_confirm_remove_keyboard(lang: str, channel_id: int) -> InlineKeyboardMarkup:
    """Keyboard to confirm channel removal."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=get_text('yes_remove', lang), 
                           callback_data=f"confirm_remove_{channel_id}"),
        InlineKeyboardButton(text=get_text('no_cancel', lang), 
                           callback_data="cancel_remove")
    )
    return builder.as_markup()
