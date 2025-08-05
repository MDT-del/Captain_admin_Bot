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
    builder.row(KeyboardButton(text=get_text('manage_payments_button', lang)))
    builder.row(
        KeyboardButton(text=get_text('set_footer_button', lang)),
        KeyboardButton(text=get_text('manage_channels_button', lang))
    )
    return builder.as_markup(resize_keyboard=True)

def get_premium_management_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Creates an inline keyboard for premium management."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=get_text('set_user_premium_button', lang), callback_data="set_premium"),
        InlineKeyboardButton(text=get_text('remove_user_premium_button', lang), callback_data="remove_premium")
    )
    builder.row(
        InlineKeyboardButton(text=get_text('check_user_info_button', lang), callback_data="check_user_info")
    )
    builder.row(
        InlineKeyboardButton(text=get_text('premium_stats_button', lang), callback_data="premium_stats")
    )
    return builder.as_markup()

def get_premium_duration_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Creates an inline keyboard for selecting premium duration."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=get_text('premium_7_days', lang), callback_data="premium_days_7"),
        InlineKeyboardButton(text=get_text('premium_30_days', lang), callback_data="premium_days_30")
    )
    builder.row(
        InlineKeyboardButton(text=get_text('premium_90_days', lang), callback_data="premium_days_90"),
        InlineKeyboardButton(text=get_text('premium_365_days', lang), callback_data="premium_days_365")
    )
    builder.row(
        InlineKeyboardButton(text=get_text('premium_custom_days', lang), callback_data="premium_custom")
    )
    builder.row(
        InlineKeyboardButton(text=get_text('back_button', lang), callback_data="back_to_premium_menu")
    )
    return builder.as_markup()

def get_user_management_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Creates an inline keyboard for user management."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=get_text('search_user_button', lang), callback_data="search_user"),
        InlineKeyboardButton(text=get_text('user_stats_button', lang), callback_data="user_stats")
    )
    builder.row(
        InlineKeyboardButton(text=get_text('broadcast_to_all_button', lang), callback_data="broadcast_all")
    )
    return builder.as_markup()

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

# --- Channel Premium Keyboards ---

def get_channel_premium_keyboard(lang: str, channels_info: List[Dict]) -> InlineKeyboardMarkup:
    """Keyboard for selecting channel to upgrade to premium."""
    builder = InlineKeyboardBuilder()
    
    for channel in channels_info:
        channel_id = channel['channel_id']
        title = channel['title']
        username = channel.get('username', f"ID: {channel_id}")
        is_premium = channel['is_premium']
        posts_count = channel['posts_this_month']
        
        if is_premium:
            text = f"💎 {title}\n{username} (پریمیوم)"
        else:
            text = f"🆓 {title}\n{username} ({posts_count}/10)"
            
        builder.row(InlineKeyboardButton(
            text=text, 
            callback_data=f"upgrade_channel_{channel_id}"
        ))
    
    return builder.as_markup()

def get_premium_duration_purchase_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Keyboard for selecting premium duration for purchase."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="💰 یک ماه - 100,000 تومان" if lang == 'fa' else "💰 1 Month - 100,000 T",
            callback_data="buy_premium_1"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="💰 سه ماه - 280,000 تومان" if lang == 'fa' else "💰 3 Months - 280,000 T", 
            callback_data="buy_premium_3"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text('back_button', lang),
            callback_data="back_to_channel_selection"
        )
    )
    
    return builder.as_markup()

def get_payment_requests_keyboard(lang: str, requests: List[Dict]) -> InlineKeyboardMarkup:
    """Keyboard for managing payment requests."""
    builder = InlineKeyboardBuilder()
    
    for request in requests:
        request_id = request['id']
        user_id = request['user_id']
        channel_title = request['channel_title']
        amount = request['amount']
        
        text = f"💳 {channel_title} - {amount:,} تومان"
        builder.row(InlineKeyboardButton(
            text=text,
            callback_data=f"view_payment_{request_id}"
        ))
    
    if not requests:
        builder.row(InlineKeyboardButton(
            text="هیچ درخواست پرداختی وجود ندارد" if lang == 'fa' else "No payment requests",
            callback_data="no_requests"
        ))
    
    return builder.as_markup()

def get_payment_approval_keyboard(lang: str, request_id: int) -> InlineKeyboardMarkup:
    """Keyboard for approving/rejecting payment requests."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="✅ تایید" if lang == 'fa' else "✅ Approve",
            callback_data=f"approve_payment_{request_id}"
        ),
        InlineKeyboardButton(
            text="❌ رد" if lang == 'fa' else "❌ Reject", 
            callback_data=f"reject_payment_{request_id}"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text('back_button', lang),
            callback_data="back_to_payments"
        )
    )
    
    return builder.as_markup()