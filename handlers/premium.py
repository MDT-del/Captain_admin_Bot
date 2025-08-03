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