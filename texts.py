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
    'main_menu': {
        'fa': "منوی اصلی:",
        'en': "Main Menu:"
    },
    'set_footer_button': {
        'fa': "تنظیم فوتر 📝",
        'en': "Set Footer 📝"
    },
    # ... (previous texts are assumed to be here) ...
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
    # ... (other channel texts) ...
    'your_channels_list': {
        'fa': "لیست کانال‌های ثبت شده شما:",
        'en': "Your registered channels:"
    },
    # Broadcasting
    'error_no_channels_for_broadcast': {
        'fa': "شما باید ابتدا حداقل یک کانال را ثبت کنید.",
        'en': "You must first register at least one channel."
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
    },
    # Scheduling
    'prompt_for_schedule_date': {
        'fa': "لطفا تاریخ ارسال را از تقویم زیر انتخاب کنید:",
        'en': "Please select the sending date from the calendar below:"
    },
    'prompt_for_schedule_time': {
        'fa': "تاریخ {date} انتخاب شد. \nحالا لطفا ساعت و دقیقه ارسال را به وقت تهران و با فرمت HH:MM (مثلا 14:30) وارد کنید:",
        'en': "Date {date} selected. \nNow please enter the sending time (Tehran time) in HH:MM format (e.g., 14:30):"
    },
    'error_invalid_time_format': {
        'fa': "❌ فرمت زمان اشتباه است. لطفا از فرمت HH:MM استفاده کنید.",
        'en': "❌ Invalid time format. Please use HH:MM format."
    },
    'schedule_success': {
        'fa': "✅ پست شما برای ارسال در تاریخ {date} ساعت {time} با موفقیت زمان‌بندی شد.",
        'en': "✅ Your post was successfully scheduled for {date} at {time}."
    },
    # Channel management
    'add_channel_prompt': {
        'fa': "لطفا ربات را به کانال مورد نظر اضافه کرده و ادمین کنید، سپس یک پیام از آن کانال فوروارد کنید:",
        'en': "Please add the bot to your channel and make it admin, then forward a message from that channel:"
    },
    'channel_added_success': {
        'fa': "✅ کانال با موفقیت اضافه شد!",
        'en': "✅ Channel added successfully!"
    },
    'channel_already_exists': {
        'fa': "❌ این کانال قبلاً ثبت شده است.",
        'en': "❌ This channel is already registered."
    },
    'channel_add_error': {
        'fa': "❌ خطا در افزودن کانال. لطفا مطمئن شوید که ربات ادمین کانال است.",
        'en': "❌ Error adding channel. Please make sure the bot is admin of the channel."
    },
    'no_channels_registered': {
        'fa': "شما هیچ کانالی ثبت نکرده‌اید.",
        'en': "You haven't registered any channels."
    },
    'remove_channel_button': {
        'fa': "🗑️ حذف کانال",
        'en': "🗑️ Remove Channel"
    },
    'channel_removed_success': {
        'fa': "✅ کانال با موفقیت حذف شد.",
        'en': "✅ Channel removed successfully."
    },
    'confirm_remove_channel': {
        'fa': "آیا مطمئن هستید که می‌خواهید این کانال را حذف کنید؟\n\n📢 {channel_title}",
        'en': "Are you sure you want to remove this channel?\n\n📢 {channel_title}"
    },
    'yes_remove': {
        'fa': "✅ بله، حذف کن",
        'en': "✅ Yes, Remove"
    },
    'no_cancel': {
        'fa': "❌ خیر، لغو",
        'en': "❌ No, Cancel"
    },
    # Premium system
    'upgrade_premium_button': {
        'fa': "💎 ارتقا به پریمیوم",
        'en': "💎 Upgrade to Premium"
    },
    'premium_info': {
        'fa': "💎 اطلاعات پریمیوم\n\n🆓 کاربران رایگان: محدود به {limit} پست در ماه\n💎 کاربران پریمیوم: ارسال نامحدود\n\n📊 شما این ماه {used} پست ارسال کرده‌اید.\n⏳ باقی‌مانده: {remaining} پست",
        'en': "💎 Premium Information\n\n🆓 Free users: Limited to {limit} posts per month\n💎 Premium users: Unlimited sending\n\n📊 You have sent {used} posts this month.\n⏳ Remaining: {remaining} posts"
    },
    'premium_info_unlimited': {
        'fa': "💎 شما کاربر پریمیوم هستید!\n\n✨ ارسال نامحدود پست\n📊 این ماه {used} پست ارسال کرده‌اید.",
        'en': "💎 You are a premium user!\n\n✨ Unlimited post sending\n📊 You have sent {used} posts this month."
    },
    'contact_developer': {
        'fa': "برای ارتقا به پریمیوم، با توسعه‌دهنده تماس بگیرید:",
        'en': "To upgrade to premium, contact the developer:"
    },
    'post_limit_reached': {
        'fa': "❌ شما به حد مجاز ارسال پست رسیده‌اید!\n\n🆓 کاربران رایگان: {limit} پست در ماه\n💎 برای ارسال نامحدود، به پریمیوم ارتقا دهید.",
        'en': "❌ You have reached your post limit!\n\n🆓 Free users: {limit} posts per month\n💎 Upgrade to premium for unlimited sending."
    },
    # Error messages
    'error_occurred': {
        'fa': "❌ خطایی رخ داد. لطفا دوباره تلاش کنید.",
        'en': "❌ An error occurred. Please try again."
    },
    'invalid_message_type': {
        'fa': "❌ نوع پیام نامعتبر است. لطفا پیام معتبری از کانال فوروارد کنید.",
        'en': "❌ Invalid message type. Please forward a valid message from the channel."
    },
    'choose_language_button': {
        'fa': "🇮🇷 فارسی",
        'en': "🇺🇸 English"
    }
}

def get_text(key, lang='en'):
    """
    Retrieves a text string from the TEXTS dictionary.
    Defaults to English if the key or language is not found.
    """
    # A simple way to avoid duplicating all keys from previous steps in the example
    all_texts = globals().get('TEXTS', {})
    return all_texts.get(key, {}).get(lang, all_texts.get(key, {}).get('en', f"No text found for key '{key}'"))
