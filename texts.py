# Centralized dictionary for all user-facing texts
TEXTS = {
    'welcome': {
        'fa': "لطفا زبان خود را انتخاب کنید.",
        'en': "Please select your language."
    },
    'lang_selected': {
        'fa': "شما زبان فارسی را انتخاب کردید. به منوی اصلی خوش آمدید!",
        'en': "You have selected English. Welcome to the main menu!"
    },
    'choose_language_button': {
        'fa': "🇮🇷 فارسی",
        'en': "🇬🇧 English"
    },
    'main_menu': {
        'fa': "شما در منوی اصلی هستید. چه کاری می‌خواهید انجام دهید؟",
        'en': "You are in the main menu. What would you like to do?"
    },
    # Footer
    'set_footer_button': {
        'fa': "تنظیم فوتر 📝",
        'en': "Set Footer 📝"
    },
    'prompt_for_footer': {
        'fa': "لطفاً متن فوتر مورد نظر خود را ارسال کنید.",
        'en': "Please send the footer text you want."
    },
    'footer_set_success': {
        'fa': "✅ فوتر شما با موفقیت تنظیم شد!",
        'en': "✅ Your footer has been set successfully!"
    },
    # Channel Management
    'manage_channels_button': {
        'fa': "مدیریت کانال‌ها 📢",
        'en': "Manage Channels 📢"
    },
    'channels_menu_title': {
        'fa': "منوی مدیریت کانال‌ها:",
        'en': "Channel Management Menu:"
    },
    'add_channel_button': {
        'fa': "➕ افزودن کانال جدید",
        'en': "➕ Add New Channel"
    },
    'my_channels_button': {
        'fa': " لیست کانال‌های من",
        'en': " My Channels"
    },
    'prompt_forward_message': {
        'fa': "برای ثبت کانال، یک پیام از کانال مورد نظر به اینجا فوروارد کنید.",
        'en': "To register a channel, please forward a message from it here."
    },
    'channel_add_success': {
        'fa': "✅ کانال با موفقیت ثبت شد!",
        'en': "✅ Channel registered successfully!"
    },
    'channel_already_registered': {
        'fa': "⚠️ این کانال قبلاً توسط شما ثبت شده است.",
        'en': "⚠️ This channel is already registered by you."
    },
    'error_not_admin_in_channel': {
        'fa': "❌ شما در این کانال ادمین نیستید. لطفا ابتدا در کانال ادمین شوید.",
        'en': "❌ You are not an admin in this channel. Please become an admin first."
    },
    'error_bot_not_admin': {
        'fa': "❌ ربات در این کانال ادمین نیست. لطفا ابتدا ربات را در کانال ادمین کنید.",
        'en': "❌ The bot is not an admin in this channel. Please make the bot an admin first."
    },
    'error_generic': {
        'fa': "خطایی رخ داد. لطفا دوباره تلاش کنید.",
        'en': "An error occurred. Please try again."
    },
    'no_channels_found': {
        'fa': "شما هنوز هیچ کانالی ثبت نکرده‌اید.",
        'en': "You haven't registered any channels yet."
    },
    'your_channels_list': {
        'fa': "لیست کانال‌های ثبت شده شما:",
        'en': "Your registered channels:"
    }
}

def get_text(key, lang='en'):
    """
    Retrieves a text string from the TEXTS dictionary.
    Defaults to English if the key or language is not found.
    """
    return TEXTS.get(key, {}).get(lang, TEXTS.get(key, {}).get('en', f"No text found for key '{key}'"))
