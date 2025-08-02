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
        'fa': "❌ شما در این کانال ادمین نیستید.",
        'en': "❌ You are not an admin in this channel."
    },
    'error_bot_not_admin': {
        'fa': "❌ ربات در این کانال ادمین نیست.",
        'en': "❌ The bot is not an admin in this channel."
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
    },
    # Broadcasting
    'error_no_channels_for_broadcast': {
        'fa': "شما باید ابتدا حداقل یک کانال را از منوی 'مدیریت کانال‌ها' ثبت کنید.",
        'en': "You must first register at least one channel from the 'Manage Channels' menu."
    },
    'post_action_menu_title': {
        'fa': "محتوای شما دریافت شد. چه کاری می‌خواهید انجام دهید؟",
        'en': "Your content has been received. What would you like to do?"
    },
    'send_now_button': { 'fa': "ارسال فوری 🚀", 'en': "Send Now 🚀" },
    'send_scheduled_button': { 'fa': "ارسال زمان‌بندی شده 🕒", 'en': "Scheduled Send 🕒" },
    'cancel_broadcast_button': { 'fa': "لغو عملیات ❌", 'en': "Cancel ❌" },
    'operation_cancelled': { 'fa': "عملیات لغو شد.", 'en': "Operation cancelled." },
    'select_channels_prompt': {
        'fa': "لطفا کانال یا کانال‌های مقصد را انتخاب کنید:",
        'en': "Please select the destination channel(s):"
    },
    'confirm_channels_button': { 'fa': "تایید و ادامه ✅", 'en': "Confirm & Continue ✅" },
    'ask_for_caption_prompt': {
        'fa': "آیا می‌خواهید برای این پست کپشن اضافه کنید؟",
        'en': "Do you want to add a caption to this post?"
    },
    'add_caption_yes_button': { 'fa': "بله، افزودن کپشن", 'en': "Yes, add caption" },
    'add_caption_no_button': { 'fa': "خیر، ارسال بدون کپشن", 'en': "No, send without caption" },
    'prompt_for_caption': {
        'fa': "لطفا متن کپشن را ارسال کنید:",
        'en': "Please send the caption text:"
    },
    'broadcast_success': {
        'fa': "✅ پست شما با موفقیت به {count} کانال ارسال شد.",
        'en': "✅ Your post was successfully sent to {count} channels."
    }
}

def get_text(key, lang='en'):
    """
    Retrieves a text string from the TEXTS dictionary.
    Defaults to English if the key or language is not found.
    """
    return TEXTS.get(key, {}).get(lang, TEXTS.get(key, {}).get('en', f"No text found for key '{key}'"))
