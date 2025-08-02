from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from texts import get_text

def get_language_keyboard() -> InlineKeyboardMarkup:
    """Creates an inline keyboard for language selection."""
    buttons = [[
        InlineKeyboardButton(text=get_text('choose_language_button', 'fa'), callback_data="lang_fa"),
        InlineKeyboardButton(text=get_text('choose_language_button', 'en'), callback_data="lang_en")
    ]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_main_menu_keyboard(lang: str) -> ReplyKeyboardMarkup:
    """Creates a reply keyboard for the main menu."""
    buttons = [
        [KeyboardButton(text=get_text('set_footer_button', lang))],
        [KeyboardButton(text=get_text('manage_channels_button', lang))]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_channels_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Creates an inline keyboard for the channel management menu."""
    buttons = [
        [InlineKeyboardButton(text=get_text('add_channel_button', lang), callback_data="add_channel")],
        [InlineKeyboardButton(text=get_text('my_channels_button', lang), callback_data="my_channels")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
