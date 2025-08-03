import logging
from aiogram import Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database
from texts import get_text
from config import FREE_USER_POST_LIMIT, DEVELOPER_ID

# All handlers for this module are registered on a separate router
router = Router()


@router.message(F.text.in_([get_text('upgrade_premium_button', 'fa'), get_text('upgrade_premium_button', 'en')]))
async def show_premium_info(message: types.Message):
    """Shows premium information and upgrade options."""
    user_id = message.from_user.id
    lang = await database.get_user_language(user_id) or 'en'
    
    try:
        is_premium = await database.is_user_premium(user_id)
        current_posts = await database.get_user_post_count_this_month(user_id)
        
        if is_premium or user_id == DEVELOPER_ID:
            # Premium user or developer
            text = get_text('premium_info_unlimited', lang).format(used=current_posts)
        else:
            # Free user
            remaining = FREE_USER_POST_LIMIT - current_posts
            text = get_text('premium_info', lang).format(
                limit=FREE_USER_POST_LIMIT,
                used=current_posts,
                remaining=max(0, remaining)
            )
            
            # Add contact info for upgrade
            text += f"\n\n{get_text('contact_developer', lang)}"
            
            # Create contact button
            builder = InlineKeyboardBuilder()
            if DEVELOPER_ID:
                builder.row(types.InlineKeyboardButton(
                    text="💬 تماس با توسعه‌دهنده" if lang == 'fa' else "💬 Contact Developer",
                    url=f"tg://user?id={DEVELOPER_ID}"
                ))
                await message.answer(text, reply_markup=builder.as_markup())
                return
        
        await message.answer(text)
        
    except Exception as e:
        logging.error(f"Error showing premium info for user {user_id}: {e}")
        await message.answer(get_text('error_occurred', lang))


@router.message(F.from_user.id == DEVELOPER_ID, F.text.startswith("/setpremium"))
async def set_premium_command(message: types.Message):
    """Developer command to set user as premium. Usage: /setpremium USER_ID [DAYS]"""
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("Usage: /setpremium USER_ID [DAYS]\nExample: /setpremium 123456789 30")
            return
            
        target_user_id = int(parts[1])
        days = int(parts[2]) if len(parts) > 2 else 365  # Default 1 year
        
        from datetime import datetime, timedelta
        premium_until = (datetime.now() + timedelta(days=days)).isoformat()
        
        await database.set_user_premium(target_user_id, premium_until)
        await message.answer(f"✅ User {target_user_id} set as premium for {days} days.")
        
        # Notify the user
        try:
            user_lang = await database.get_user_language(target_user_id) or 'en'
            notification = "🎉 تبریک! شما به پریمیوم ارتقا یافتید!" if user_lang == 'fa' else "🎉 Congratulations! You've been upgraded to premium!"
            await message.bot.send_message(target_user_id, notification)
        except Exception:
            pass  # User might have blocked the bot
            
    except (ValueError, IndexError):
        await message.answer("Invalid format. Usage: /setpremium USER_ID [DAYS]")
    except Exception as e:
        logging.error(f"Error setting premium: {e}")
        await message.answer(f"Error: {e}")


@router.message(F.from_user.id == DEVELOPER_ID, F.text.startswith("/removepremium"))
async def remove_premium_command(message: types.Message):
    """Developer command to remove premium from user. Usage: /removepremium USER_ID"""
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("Usage: /removepremium USER_ID")
            return
            
        target_user_id = int(parts[1])
        
        # Set premium to 0 and clear premium_until
        await database.set_user_premium(target_user_id, None)
        # Also update is_premium to 0
        import aiosqlite
        async with aiosqlite.connect(database.DB_NAME) as db:
            await db.execute('UPDATE users SET is_premium = 0 WHERE user_id = ?', (target_user_id,))
            await db.commit()
            
        await message.answer(f"✅ Premium removed from user {target_user_id}.")
        
        # Notify the user
        try:
            user_lang = await database.get_user_language(target_user_id) or 'en'
            notification = "📢 اشتراک پریمیوم شما به پایان رسید." if user_lang == 'fa' else "📢 Your premium subscription has ended."
            await message.bot.send_message(target_user_id, notification)
        except Exception:
            pass  # User might have blocked the bot
            
    except (ValueError, IndexError):
        await message.answer("Invalid format. Usage: /removepremium USER_ID")
    except Exception as e:
        logging.error(f"Error removing premium: {e}")
        await message.answer(f"Error: {e}")


@router.message(F.text.in_([get_text('developer_stats_button', 'fa'), get_text('developer_stats_button', 'en')]))
async def show_stats_menu(message: types.Message):
    """Shows bot statistics for developer."""
    user_id = message.from_user.id
    if user_id != DEVELOPER_ID:
        return
        
    await show_stats_command(message)

@router.message(F.from_user.id == DEVELOPER_ID, F.text.startswith("/stats"))
async def show_stats_command(message: types.Message):
    """Developer command to show bot statistics."""
    try:
        import aiosqlite
        async with aiosqlite.connect(database.DB_NAME) as db:
            # Total users
            cursor = await db.execute('SELECT COUNT(*) FROM users')
            total_users = (await cursor.fetchone())[0]
            
            # Premium users
            cursor = await db.execute('SELECT COUNT(*) FROM users WHERE is_premium = 1')
            premium_users = (await cursor.fetchone())[0]
            
            # Total channels
            cursor = await db.execute('SELECT COUNT(*) FROM channels')
            total_channels = (await cursor.fetchone())[0]
            
            # Total posts sent
            cursor = await db.execute('SELECT SUM(total_posts_sent) FROM user_stats')
            result = await cursor.fetchone()
            total_posts = result[0] if result[0] else 0
            
            # Posts this month
            cursor = await db.execute('SELECT SUM(posts_sent_this_month) FROM user_stats')
            result = await cursor.fetchone()
            posts_this_month = result[0] if result[0] else 0
            
        stats_text = f"""📊 Bot Statistics:

👥 Total Users: {total_users}
💎 Premium Users: {premium_users}
📢 Total Channels: {total_channels}
📨 Total Posts Sent: {total_posts}
📅 Posts This Month: {posts_this_month}
🆓 Free Users: {total_users - premium_users}"""

        await message.answer(stats_text)
        
    except Exception as e:
        logging.error(f"Error showing stats: {e}")
        await message.answer(f"Error: {e}")


@router.message(F.text.in_([get_text('developer_manage_users_button', 'fa'), get_text('developer_manage_users_button', 'en')]))
async def show_user_management_menu(message: types.Message):
    """Shows user management options for developer."""
    user_id = message.from_user.id
    if user_id != DEVELOPER_ID:
        return
        
    lang = await database.get_user_language(user_id) or 'en'
    
    help_text = """🔧 دستورات مدیریت کاربران:

/setpremium USER_ID [DAYS] - تنظیم پریمیوم
مثال: /setpremium 123456789 30

/removepremium USER_ID - حذف پریمیوم
مثال: /removepremium 123456789

/userinfo USER_ID - اطلاعات کاربر
مثال: /userinfo 123456789""" if lang == 'fa' else """🔧 User Management Commands:

/setpremium USER_ID [DAYS] - Set premium
Example: /setpremium 123456789 30

/removepremium USER_ID - Remove premium
Example: /removepremium 123456789

/userinfo USER_ID - User information
Example: /userinfo 123456789"""

    await message.answer(help_text)


@router.message(F.from_user.id == DEVELOPER_ID, F.text.startswith("/userinfo"))
async def show_user_info(message: types.Message):
    """Shows information about a specific user."""
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("Usage: /userinfo USER_ID")
            return
            
        target_user_id = int(parts[1])
        
        import aiosqlite
        async with aiosqlite.connect(database.DB_NAME) as db:
            # Get user info
            cursor = await db.execute('''
                SELECT u.user_id, u.language_code, u.is_premium, u.premium_until, u.created_at,
                       s.posts_sent_this_month, s.total_posts_sent
                FROM users u
                LEFT JOIN user_stats s ON u.user_id = s.user_id
                WHERE u.user_id = ?
            ''', (target_user_id,))
            user_data = await cursor.fetchone()
            
            if not user_data:
                await message.answer(f"❌ User {target_user_id} not found.")
                return
                
            # Get user channels count
            cursor = await db.execute('SELECT COUNT(*) FROM channels WHERE user_id = ?', (target_user_id,))
            channels_count = (await cursor.fetchone())[0]
            
        user_id, lang_code, is_premium, premium_until, created_at, posts_month, total_posts = user_data
        
        info_text = f"""👤 User Information:

🆔 User ID: {user_id}
🌐 Language: {lang_code or 'Not set'}
💎 Premium: {'Yes' if is_premium else 'No'}
📅 Premium Until: {premium_until or 'N/A'}
📊 Posts This Month: {posts_month or 0}
📈 Total Posts: {total_posts or 0}
📢 Channels: {channels_count}
🗓️ Joined: {created_at or 'Unknown'}"""

        await message.answer(info_text)
        
    except (ValueError, IndexError):
        await message.answer("Invalid format. Usage: /userinfo USER_ID")
    except Exception as e:
        logging.error(f"Error showing user info: {e}")
        await message.answer(f"Error: {e}")