# Centralized dictionary for all user-facing texts
# This makes it easy to manage and add new languages

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
    'set_footer_button': {
        'fa': "تنظیم فوتر 📝",
        'en': "Set Footer 📝"
    },
    'prompt_for_footer': {
        'fa': "لطفاً متن فوتر مورد نظر خود را ارسال کنید. این متن به انتهای تمام پست‌های شما اضافه خواهد شد.",
        'en': "Please send the footer text you want. This text will be added to the end of all your posts."
    },
    'footer_set_success': {
        'fa': "✅ فوتر شما با موفقیت تنظیم شد!",
        'en': "✅ Your footer has been set successfully!"
    }
}

def get_text(key, lang='en'):
    """
    Retrieves a text string from the TEXTS dictionary.
    Defaults to English if the key or language is not found.
    """
    return TEXTS.get(key, {}).get(lang, TEXTS.get(key, {}).get('en', f"No text found for key '{key}'"))
