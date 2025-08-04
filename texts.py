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
        'fa': "❌ شما به حد مجاز ارسال پست رسیده‌اید!\n\n🆓 کاربران رایگان: {limit} پست در ماه\n�� برای ارسال نامحدود، به پریمیوم ارتقا دهید.",
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
    },
    # Footer management
    'prompt_for_footer': {
        'fa': "لطفا متن فوتر جدید را ارسال کنید:",
        'en': "Please send the new footer text:"
    },
    'footer_set_success': {
        'fa': "✅ فوتر با موفقیت تنظیم شد!",
        'en': "✅ Footer set successfully!"
    },
    # Developer menu
    'developer_menu': {
        'fa': "🔧 منوی توسعه‌دهنده\n\nشما به عنوان توسعه‌دهنده وارد شده‌اید.",
        'en': "🔧 Developer Menu\n\nYou are logged in as developer."
    },
    'developer_stats_button': {
        'fa': "📊 آمار و گزارشات",
        'en': "📊 Statistics & Reports"
    },
    'developer_manage_users_button': {
        'fa': "👥 مدیریت کاربران",
        'en': "👥 Manage Users"
    },
    'developer_premium_management_button': {
        'fa': "💎 مدیریت پریمیوم",
        'en': "💎 Premium Management"
    },
    'manage_payments_button': {
        'fa': "💳 مدیریت پرداخت‌ها",
        'en': "💳 Manage Payments"
    },
    # Premium Management Menu
    'set_user_premium_button': {
        'fa': "➕ پریمیوم کردن کاربر",
        'en': "➕ Set User Premium"
    },
    'remove_user_premium_button': {
        'fa': "➖ حذف پریمیوم کاربر",
        'en': "➖ Remove User Premium"
    },
    'check_user_info_button': {
        'fa': "👤 اطلاعات کاربر",
        'en': "👤 User Information"
    },
    'premium_stats_button': {
        'fa': "📊 آمار پریمیوم",
        'en': "📊 Premium Statistics"
    },
    'search_user_button': {
        'fa': "🔍 جستجوی کاربر",
        'en': "🔍 Search User"
    },
    'user_stats_button': {
        'fa': "📈 آمار کاربران",
        'en': "📈 User Statistics"
    },
    'broadcast_to_all_button': {
        'fa': "📢 پیام همگانی",
        'en': "📢 Broadcast to All"
    },
    'back_button': {
        'fa': "🔙 بازگشت",
        'en': "🔙 Back"
    },
    # Premium Duration Options
    'premium_7_days': {
        'fa': "7️⃣ یک هفته",
        'en': "7️⃣ 7 Days"
    },
    'premium_30_days': {
        'fa': "3️⃣0️⃣ یک ماه",
        'en': "3️⃣0️⃣ 30 Days"
    },
    'premium_90_days': {
        'fa': "9️⃣0️⃣ سه ماه",
        'en': "9️⃣0️⃣ 90 Days"
    },
    'premium_365_days': {
        'fa': "🗓️ یک سال",
        'en': "🗓️ 365 Days"
    },
    'premium_custom_days': {
        'fa': "⚙️ تعداد روز دلخواه",
        'en': "⚙️ Custom Days"
    },
    # Premium Management Messages
    'premium_management_menu': {
        'fa': "💎 منوی مدیریت پریمیوم\n\nلطفا یکی از گزینه‌های زیر را انتخاب کنید:",
        'en': "💎 Premium Management Menu\n\nPlease select one of the options below:"
    },
    'enter_user_id_for_premium': {
        'fa': "لطفا شناسه کاربری (User ID) کاربر مورد نظر ��ا وارد کنید:",
        'en': "Please enter the User ID of the target user:"
    },
    'select_premium_duration': {
        'fa': "مدت زمان پریمیوم را انتخاب کنید:",
        'en': "Select premium duration:"
    },
    'enter_custom_days': {
        'fa': "تعداد روزهای پریمیوم را وارد کنید (عدد):",
        'en': "Enter the number of premium days (number):"
    },
    'premium_set_success': {
        'fa': "✅ کاربر {user_id} با موفقیت به مدت {days} روز پریمیوم شد.",
        'en': "✅ User {user_id} has been set as premium for {days} days."
    },
    'premium_removed_success': {
        'fa': "✅ پریمیوم کاربر {user_id} با موفقیت حذف شد.",
        'en': "✅ Premium removed from user {user_id} successfully."
    },
    'user_not_found': {
        'fa': "❌ کاربر یافت نشد.",
        'en': "❌ User not found."
    },
    'invalid_user_id': {
        'fa': "❌ شناسه کاربری نامعتبر است.",
        'en': "❌ Invalid user ID."
    },
    'invalid_days_number': {
        'fa': "❌ تعداد روزها نامعتبر است. لطفا یک عدد وارد کنید.",
        'en': "❌ Invalid number of days. Please enter a number."
    },
    'premium_notification_granted': {
        'fa': "🎉 تبریک! شما به پریمیوم ارتقا یافتید!\n\n✨ از این پس می‌توانید پست‌های نامحدود ارسال کنید.",
        'en': "🎉 Congratulations! You've been upgraded to premium!\n\n✨ You can now send unlimited posts."
    },
    'premium_notification_removed': {
        'fa': "📢 اشتراک پریمیوم شما به پایان رسید.\n\n🆓 شما دوباره به حسا�� رایگان بازگشتید.",
        'en': "📢 Your premium subscription has ended.\n\n🆓 You're back to the free account."
    },
    # Channel Premium System
    'channel_premium_info': {
        'fa': "💎 سیستم پریمیوم کانال محور\n\n🆓 هر کانال: 10 پست رایگان در ماه\n💎 کانال پریمیوم: ارسال نامحدود\n\n📊 وضعیت کانال‌های شما:",
        'en': "💎 Channel-based Premium System\n\n🆓 Each channel: 10 free posts per month\n💎 Premium channel: Unlimited posts\n\n📊 Your channels status:"
    },
    'select_channel_for_premium': {
        'fa': "لطفا کانالی که می‌خواهید پریمیوم کنید را انتخاب کنید:",
        'en': "Please select the channel you want to upgrade to premium:"
    },
    'select_premium_duration_purchase': {
        'fa': "مدت زمان پریمیوم را انتخاب کنید:",
        'en': "Select premium duration:"
    },
    'payment_info': {
        'fa': "💳 اطلاعات پرداخت\n\n🏦 شماره کارت: {card_number}\n👤 نام صاحب کارت: {card_holder}\n💰 مبلغ: {amount:,} تومان\n📅 مدت: {duration} ماه\n📺 کانال: {channel_title}\n\n📝 لطفا مبلغ را واریز کرده و عکس رسید را ارسال کنید.",
        'en': "💳 Payment Information\n\n🏦 Card Number: {card_number}\n👤 Card Holder: {card_holder}\n💰 Amount: {amount:,} Toman\n📅 Duration: {duration} months\n📺 Channel: {channel_title}\n\n📝 Please transfer the amount and send the receipt photo."
    },
    'waiting_for_receipt': {
        'fa': "📸 لطفا عکس رسید پرداخت را ارسال کنید:",
        'en': "📸 Please send the payment receipt photo:"
    },
    'receipt_received': {
        'fa': "✅ رسید شما دریافت شد و برای بررسی ارسال شد.\n\n⏳ لطفا منتظر تایید باشید. پس از تایید، کانال شما پریمیوم خواهد شد.",
        'en': "✅ Your receipt has been received and sent for review.\n\n⏳ Please wait for approval. After approval, your channel will be premium."
    },
    'payment_approved': {
        'fa': "🎉 پرداخت شما تایید شد!\n\n💎 کانال {channel_title} به مدت {duration} ماه پریمیوم شد.\n\n✨ حالا می‌توانید پست‌های نامحدود ارسال کنید!",
        'en': "🎉 Your payment has been approved!\n\n💎 Channel {channel_title} is now premium for {duration} months.\n\n✨ You can now send unlimited posts!"
    },
    'payment_rejected': {
        'fa': "❌ متأسفانه پرداخت شما تایید نشد.\n\n📞 لطفا با پشتیبانی تماس بگیرید.",
        'en': "❌ Unfortunately, your payment was not approved.\n\n📞 Please contact support."
    },
    'payment_requests_title': {
        'fa': "💳 درخواست‌های پرداخت",
        'en': "💳 Payment Requests"
    },
    'payment_request_details': {
        'fa': "💳 جزئیات درخواست پرداخت\n\n👤 کاربر: {user_id}\n📺 کانال: {channel_title}\n💰 مبلغ: {amount:,} تومان\n📅 مدت: {duration} ماه\n🕐 تاریخ: {date}\n\n📸 رسید پرداخت:",
        'en': "💳 Payment Request Details\n\n👤 User: {user_id}\n📺 Channel: {channel_title}\n💰 Amount: {amount:,} Toman\n📅 Duration: {duration} months\n🕐 Date: {date}\n\n📸 Payment Receipt:"
    },
    'no_payment_requests': {
        'fa': "هیچ درخواست پرداختی وجود ندارد.",
        'en': "No payment requests available."
    },
    'channel_already_premium': {
        'fa': "💎 این کانال در حال حاضر پریمیوم است!",
        'en': "💎 This channel is already premium!"
    },
    'invalid_receipt': {
        'fa': "❌ لطفا یک عکس معتبر از رسید پرداخت ارسال کنید.",
        'en': "❌ Please send a valid payment receipt photo."
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