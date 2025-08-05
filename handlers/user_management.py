import logging
from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext

import database
from texts import get_text
from states import Form
from keyboards import get_user_management_keyboard
from config import DEVELOPER_ID

router = Router()

# --- User Management Handlers ---

@router.callback_query(F.data == "search_user")
async def search_user_handler(callback: types.CallbackQuery, state: FSMContext):
    """Start user search process."""
    if callback.from_user.id != DEVELOPER_ID:
        await callback.answer("❌ Access denied", show_alert=True)
        return
    
    await state.set_state(Form.waiting_for_user_id_info)
    await callback.message.edit_text("🔍 لطفا شناسه کاربری (User ID) کاربر مورد نظر را وارد کنید:")

@router.callback_query(F.data == "user_stats")
async def user_stats_handler(callback: types.CallbackQuery):
    """Show detailed user statistics."""
    if callback.from_user.id != DEVELOPER_ID:
        await callback.answer("❌ Access denied", show_alert=True)
        return
    
    try:
        import aiosqlite
        async with aiosqlite.connect(database.DB_NAME) as db:
            # Get detailed user statistics
            cursor = await db.execute('''
                SELECT 
                    COUNT(*) as total_users,
                    COUNT(CASE WHEN is_premium = 1 THEN 1 END) as premium_users,
                    AVG(CASE WHEN s.posts_sent_this_month IS NOT NULL THEN s.posts_sent_this_month ELSE 0 END) as avg_posts_month,
                    MAX(s.posts_sent_this_month) as max_posts_month,
                    COUNT(CASE WHEN s.posts_sent_this_month > 0 THEN 1 END) as active_users
                FROM users u
                LEFT JOIN user_stats s ON u.user_id = s.user_id
            ''')
            stats = await cursor.fetchone()
            
            # Get channel statistics with proper premium check
            cursor = await db.execute('''
                SELECT 
                    COUNT(*) as total_channels,
                    COUNT(CASE WHEN cp.is_premium = 1 AND cp.premium_until > ? THEN 1 END) as premium_channels,
                    AVG(cp.posts_sent_this_month) as avg_channel_posts
                FROM channels c
                LEFT JOIN channel_premium cp ON c.channel_id = cp.channel_id AND c.user_id = cp.user_id
            ''', (database.get_tehran_time().isoformat(),))
            channel_stats = await cursor.fetchone()
            
            # Get recent activity
            cursor = await db.execute('''
                SELECT COUNT(*) FROM users WHERE created_at > datetime('now', '-7 days')
            ''')
            new_users_week = (await cursor.fetchone())[0]
            
            # Get payment statistics
            cursor = await db.execute('''
                SELECT 
                    COUNT(*) as total_payments,
                    COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved_payments,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_payments,
                    SUM(CASE WHEN status = 'approved' THEN amount ELSE 0 END) as total_revenue
                FROM payment_requests
            ''')
            payment_stats = await cursor.fetchone()
            
        total_users, premium_users, avg_posts, max_posts, active_users = stats
        total_channels, premium_channels, avg_channel_posts = channel_stats
        total_payments, approved_payments, pending_payments, total_revenue = payment_stats or (0, 0, 0, 0)
        
        stats_text = f"""📊 آمار تفصیلی سیستم:

👥 **کاربران:**
├── کل کاربران: {total_users}
├── کاربران پریمیوم: {premium_users}
├── کاربران رایگان: {total_users - premium_users}
├── کاربران فعال: {active_users}
└── کاربران جدید (هفته): {new_users_week}

📢 **کانال‌ها:**
├── کل کانال‌ها: {total_channels}
├── کانال‌های پریمیوم: {premium_channels or 0}
└── کانال‌های رایگان: {total_channels - (premium_channels or 0)}

📈 **فعالیت:**
├── میانگین پست/کاربر: {avg_posts:.1f}
├── بیشترین پست ماهانه: {max_posts or 0}
└── میانگین پست/کانال: {avg_channel_posts or 0:.1f}

💰 **درآمد:**
├── کل پرداخت‌ها: {total_payments}
├── پرداخت‌های تایید شده: {approved_payments}
├── پرداخت‌های در انتظار: {pending_payments}
└── کل درآمد: {total_revenue:,} تومان

📊 **نرخ‌ها:**
├── نرخ پریمیوم کاربران: {(premium_users/total_users*100) if total_users > 0 else 0:.1f}%
├── نرخ پریمیوم کانال‌ها: {((premium_channels or 0)/total_channels*100) if total_channels > 0 else 0:.1f}%
└── نرخ تایید پرداخت: {(approved_payments/total_payments*100) if total_payments > 0 else 0:.1f}%"""

        await callback.message.edit_text(stats_text)
        
    except Exception as e:
        logging.error(f"Error showing user stats: {e}")
        await callback.message.edit_text(f"❌ خطا: {e}")

@router.callback_query(F.data == "broadcast_all")
async def broadcast_all_handler(callback: types.CallbackQuery, state: FSMContext):
    """Start broadcast to all users process."""
    if callback.from_user.id != DEVELOPER_ID:
        await callback.answer("❌ Access denied", show_alert=True)
        return
    
    await state.set_state(Form.waiting_for_broadcast_message)
    await callback.message.edit_text(
        "📢 پیام همگانی\n\n"
        "لطفا پیامی که می‌خواهید به همه کاربران ارسال شود را بنویسید:\n\n"
        "⚠️ این پیام به همه کاربران ربات ارسال خواهد شد!"
    )

@router.message(Form.waiting_for_broadcast_message)
async def process_broadcast_message(message: types.Message, state: FSMContext, bot: Bot):
    """Process and send broadcast message to all users."""
    if message.from_user.id != DEVELOPER_ID:
        return
    
    try:
        # Get all users
        import aiosqlite
        async with aiosqlite.connect(database.DB_NAME) as db:
            cursor = await db.execute('SELECT user_id FROM users')
            users = await cursor.fetchall()
        
        if not users:
            await message.answer("❌ هیچ کاربری یافت نشد.")
            await state.clear()
            return
        
        # Confirm broadcast
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        builder = InlineKeyboardBuilder()
        builder.row(
            types.InlineKeyboardButton(text="✅ تایید ارسال", callback_data="confirm_broadcast"),
            types.InlineKeyboardButton(text="❌ لغو", callback_data="cancel_broadcast_all")
        )
        
        await state.update_data(broadcast_message=message.text, broadcast_users=len(users))
        
        await message.answer(
            f"📢 آماده ارسال پیام همگانی\n\n"
            f"📝 پیام: {message.text[:100]}{'...' if len(message.text) > 100 else ''}\n"
            f"👥 تعداد کاربران: {len(users)}\n\n"
            f"آیا مطمئن هستید؟",
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logging.error(f"Error preparing broadcast: {e}")
        await message.answer(f"❌ خطا: {e}")
        await state.clear()

@router.callback_query(F.data == "confirm_broadcast")
async def confirm_broadcast(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Confirm and execute broadcast."""
    if callback.from_user.id != DEVELOPER_ID:
        await callback.answer("❌ Access denied", show_alert=True)
        return
    
    try:
        data = await state.get_data()
        broadcast_message = data.get('broadcast_message')
        
        if not broadcast_message:
            await callback.message.edit_text("❌ خطا: پیام یافت نشد")
            return
        
        # Get all users
        import aiosqlite
        async with aiosqlite.connect(database.DB_NAME) as db:
            cursor = await db.execute('SELECT user_id FROM users')
            users = await cursor.fetchall()
        
        await callback.message.edit_text("📤 در حال ارسال پیام همگانی...")
        
        # Send to all users
        sent_count = 0
        failed_count = 0
        
        for user in users:
            user_id = user[0]
            try:
                await bot.send_message(user_id, f"📢 پیام از مدیریت:\n\n{broadcast_message}")
                sent_count += 1
            except Exception as e:
                failed_count += 1
                logging.warning(f"Failed to send broadcast to user {user_id}: {e}")
        
        result_text = f"""✅ ارسال پیام همگانی تکمیل شد

📊 نتایج:
├── ارسال موفق: {sent_count}
├── ارسال ناموفق: {failed_count}
└── کل: {sent_count + failed_count}

📈 نرخ موفقیت: {(sent_count/(sent_count + failed_count)*100):.1f}%"""

        await callback.message.edit_text(result_text)
        await state.clear()
        
    except Exception as e:
        logging.error(f"Error executing broadcast: {e}")
        await callback.message.edit_text(f"❌ خطا در ارسال: {e}")
        await state.clear()

@router.callback_query(F.data == "cancel_broadcast_all")
async def cancel_broadcast(callback: types.CallbackQuery, state: FSMContext):
    """Cancel broadcast."""
    if callback.from_user.id != DEVELOPER_ID:
        await callback.answer("❌ Access denied", show_alert=True)
        return
    
    await state.clear()
    await callback.message.edit_text("❌ ارسال پیام همگانی لغو شد.")

# --- Top Users Handler ---

@router.message(F.from_user.id == DEVELOPER_ID, F.text.startswith("/topusers"))
async def show_top_users(message: types.Message):
    """Show top users by activity."""
    try:
        import aiosqlite
        async with aiosqlite.connect(database.DB_NAME) as db:
            # Top users by posts
            cursor = await db.execute('''
                SELECT u.user_id, u.language_code, s.total_posts_sent, s.posts_sent_this_month
                FROM users u
                LEFT JOIN user_stats s ON u.user_id = s.user_id
                WHERE s.total_posts_sent > 0
                ORDER BY s.total_posts_sent DESC
                LIMIT 10
            ''')
            top_users = await cursor.fetchall()
            
            if not top_users:
                await message.answer("📊 هیچ کاربر فعالی یافت نشد.")
                return
            
            text = "🏆 برترین کاربران (بر اساس کل پست‌ها):\n\n"
            
            for i, user in enumerate(top_users, 1):
                user_id, lang, total_posts, month_posts = user
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}️⃣"
                text += f"{emoji} کاربر {user_id}\n"
                text += f"   📊 کل پست‌ها: {total_posts or 0}\n"
                text += f"   📅 این ماه: {month_posts or 0}\n"
                text += f"   🌐 زب��ن: {lang or 'نامشخص'}\n\n"
            
            await message.answer(text)
            
    except Exception as e:
        logging.error(f"Error showing top users: {e}")
        await message.answer(f"❌ خطا: {e}")

@router.message(F.from_user.id == DEVELOPER_ID, F.text.startswith("/activeusers"))
async def show_active_users(message: types.Message):
    """Show recently active users."""
    try:
        import aiosqlite
        async with aiosqlite.connect(database.DB_NAME) as db:
            # Recently active users
            cursor = await db.execute('''
                SELECT u.user_id, u.language_code, u.created_at, s.posts_sent_this_month
                FROM users u
                LEFT JOIN user_stats s ON u.user_id = s.user_id
                WHERE u.created_at > datetime('now', '-7 days') OR s.posts_sent_this_month > 0
                ORDER BY u.created_at DESC
                LIMIT 20
            ''')
            active_users = await cursor.fetchall()
            
            if not active_users:
                await message.answer("📊 هیچ کاربر فعالی یافت نشد.")
                return
            
            text = "🔥 کاربران فعال (7 روز گذشته):\n\n"
            
            for user in active_users:
                user_id, lang, created_at, month_posts = user
                # Format date to Persian
                created_persian = database.format_persian_date(created_at) if created_at else 'نامشخص'
                text += f"👤 کاربر {user_id}\n"
                text += f"   📅 عضویت: {created_persian}\n"
                text += f"   📊 پست‌های ماه: {month_posts or 0}\n"
                text += f"   🌐 زبان: {lang or 'نامشخص'}\n\n"
            
            await message.answer(text)
            
    except Exception as e:
        logging.error(f"Error showing active users: {e}")
        await message.answer(f"❌ خطا: {e}")

@router.message(F.from_user.id == DEVELOPER_ID, F.text.startswith("/premiumchannels"))
async def show_premium_channels(message: types.Message):
    """Show all premium channels with expiry dates."""
    try:
        import aiosqlite
        async with aiosqlite.connect(database.DB_NAME) as db:
            # Get premium channels
            cursor = await db.execute('''
                SELECT cp.channel_id, cp.user_id, cp.premium_until, cp.created_at
                FROM channel_premium cp
                WHERE cp.is_premium = 1 AND cp.premium_until > ?
                ORDER BY cp.premium_until ASC
            ''', (database.get_tehran_time().isoformat(),))
            premium_channels = await cursor.fetchall()
            
            if not premium_channels:
                await message.answer("📊 هیچ کانال پریمیومی یافت نشد.")
                return
            
            text = "💎 کانال‌های پریمیوم:\n\n"
            
            for channel in premium_channels:
                channel_id, user_id, premium_until, created_at = channel
                
                # Format dates to Persian
                expiry_persian = database.format_persian_date(premium_until) if premium_until else 'نامشخص'
                created_persian = database.format_persian_date(created_at) if created_at else 'نامشخص'
                
                text += f"📢 کانال {channel_id}\n"
                text += f"   👤 کاربر: {user_id}\n"
                text += f"   📅 ثبت: {created_persian}\n"
                text += f"   ⏰ انقضا: {expiry_persian}\n\n"
            
            text += f"📊 کل کانال‌های پریمیوم: {len(premium_channels)}"
            
            await message.answer(text)
            
    except Exception as e:
        logging.error(f"Error showing premium channels: {e}")
        await message.answer(f"❌ خطا: {e}")