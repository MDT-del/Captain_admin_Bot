# Centralized dictionary for all user-facing texts
# This makes it easy to manage and add new languages

TEXTS = {
    'welcome': {
        'fa': "لطفا زبان خود را انتخاب کنید.",
        'en': "Please select your language."
    },
    'lang_selected': {
        'fa': "شما زبان فارسی را انتخاب کردید. خوش آمدید!",
        'en': "You have selected English. Welcome!"
    },
    'choose_language_button': {
        'fa': "🇮🇷 فارسی",
        'en': "🇬🇧 English"
    }
}

def get_text(key, lang='en'):
    """
    Retrieves a text string from the TEXTS dictionary.
    Defaults to English if the key or language is not found.
    """
    return TEXTS.get(key, {}).get(lang, TEXTS.get(key, {}).get('en', f"No text found for key '{key}'"))
