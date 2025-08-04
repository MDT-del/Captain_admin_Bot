import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database
from texts import get_text
from states import Form
from keyboards import get_premium_management_keyboard, get_premium_duration_keyboard, get_user_management_keyboard
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


# --- Developer Premium Management Menu ---

@router.message(F.text.in_([get_text('developer_premium_management_button', 'fa'), get_text('developer_premium_management_button', 'en')]))
async def show_premium_management_menu(message: types.Message):
    """Shows premium management menu for developer."""
    user_id = message.from_user.id
    if user_id != DEVELOPER_ID:
        return
        
    lang = await database.get_user_language(user_id) or 'en'
    
    await message.answer(
        get_text('premium_management_menu', lang),
        reply_markup=get_premium_management_keyboard(lang)
    )


@router.callback_query(F.data == "set_premium")
async def start_set_premium(callback: types.CallbackQuery, state: FSMContext):
    """Start the process of setting a user as premium."""
    if callback.from_user.id != DEVELOPER_ID:
        await callback.answer("❌ Access denied", show_alert=True)
        return
        
    lang = await database.get_user_language(callback.from_user.id) or 'en'
    await state.set_state(Form.waiting_for_user_id_premium)
    
    await callback.message.edit_text(get_text('enter_user_id_for_premium', lang))


@router.message(Form.waiting_for_user_id_premium, F.text)
async def process_user_id_for_premium(message: types.Message, state: FSMContext):
    """Process user ID for premium setting."""
    if message.from_user.id != DEVELOPER_ID:
        return
        
    lang = await database.get_user_language(message.from_user.id) or 'en'
    
    try:
        user_id = int(message.text.strip())
        await state.update_data(target_user_id=user_id)
        await state.set_state(None)
        
        # Check if user exists
        user_lang = await database.get_user_language(user_id)
        if not user_lang:
            await message.answer(get_text('user_not_found', lang))
            return
            
        await message.answer(
            get_text('select_premium_duration', lang),
            reply_markup=get_premium_duration_keyboard(lang)
        )
        
    except ValueError:
        await message.answer(get_text('invalid_user_id', lang))


@router.callback_query(F.data.startswith("premium_days_"))
async def process_premium_duration(callback: types.CallbackQuery, state: FSMContext):
    """Process premium duration selection."""
    if callback.from_user.id != DEVELOPER_ID:
        await callback.answer("❌ Access denied", show_alert=True)
        return
        
    lang = await database.get_user_language(callback.from_user.id) or 'en'
    data = await state.get_data()
    target_user_id = data.get('target_user_id')
    
    if not target_user_id:
        await callback.message.edit_text("❌ خطا: شناسه کاربر یافت نشد")
        return
    
    days_str = callback.data.split("_")[2]
    
    if days_str == "custom":
        await state.set_state(Form.waiting_for_custom_days)
        await callback.message.edit_text(get_text('enter_custom_days', lang))
        return
    
    try:
        days = int(days_str)
        await set_user_premium_with_days(callback.message, target_user_id, days, lang)
        await state.clear()
        
    except ValueError:
        await callback.message.edit_text("❌ خطا در پردازش تعداد روزها")


@router.message(Form.waiting_for_custom_days, F.text)
async def process_custom_days(message: types.Message, state: FSMContext):
    """Process custom premium days."""
    if message.from_user.id != DEVELOPER_ID:
        return
        
    lang = await database.get_user_language(message.from_user.id) or 'en'
    data = await state.get_data()
    target_user_id = data.get('target_user_id')
    
    if not target_user_id:
        await message.answer("❌ خطا: شناسه کاربر یافت نشد")
        return
    
    try:
        days = int(message.text.strip())
        if days <= 0:
            await message.answer(get_text('invalid_days_number', lang))
            return
            
        await set_user_premium_with_days(message, target_user_id, days, lang)
        await state.clear()
        
    except ValueError:
        await message.answer(get_text('invalid_days_number', lang))


async def set_user_premium_with_days(message, target_user_id: int, days: int, lang: str):
    """Helper function to set user premium with specified days."""
    try:
        from datetime import datetime, timedelta
        premium_until = (datetime.now() + timedelta(days=days)).isoformat()
        
        await database.set_user_premium(target_user_id, premium_until)
        
        success_text = get_text('premium_set_success', lang).format(
            user_id=target_user_id, 
            days=days
        )
        await message.answer(success_text)
        
        # Notify the user
        try:
            user_lang = await database.get_user_language(target_user_id) or 'en'
            notification = get_text('premium_notification_granted', user_lang)
            await message.bot.send_message(target_user_id, notification)
        except Exception:
            pass  # User might have blocked the bot
            
    except Exception as e:
        logging.error(f"Error setting premium: {e}")
        await message.answer(f"❌ خطا: {e}")


@router.callback_query(F.data == "remove_premium")
async def start_remove_premium(callback: types.CallbackQuery, state: FSMContext):
    """Start the process of removing premium from a user."""
    if callback.from_user.id != DEVELOPER_ID:
        await callback.answer("❌ Access denied", show_alert=True)
        return
        
    lang = await database.get_user_language(callback.from_user.id) or 'en'
    await state.set_state(Form.waiting_for_user_id_remove_premium)
    
    await callback.message.edit_text(get_text('enter_user_id_for_premium', lang))


@router.message(Form.waiting_for_user_id_remove_premium, F.text)
async def process_remove_premium(message: types.Message, state: FSMContext):
    """Process premium removal."""
    if message.from_user.id != DEVELOPER_ID:
        return
        
    lang = await database.get_user_language(message.from_user.id) or 'en'
    
    try:
        target_user_id = int(message.text.strip())
        
        # Check if user exists
        user_lang = await database.get_user_language(target_user_id)
        if not user_lang:
            await message.answer(get_text('user_not_found', lang))
            return
        
        # Remove premium
        await database.set_user_premium(target_user_id, None)
        
        # Also update is_premium to 0
        import aiosqlite
        async with aiosqlite.connect(database.DB_NAME) as db:
            await db.execute('UPDATE users SET is_premium = 0 WHERE user_id = ?', (target_user_id,))
            await db.commit()
            
        success_text = get_text('premium_removed_success', lang).format(user_id=target_user_id)
        await message.answer(success_text)
        
        # Notify the user
        try:
            notification = get_text('premium_notification_removed', user_lang)
            await message.bot.send_message(target_user_id, notification)
        except Exception:
            pass  # User might have blocked the bot
            
        await state.clear()
        
    except ValueError:
        await message.answer(get_text('invalid_user_id', lang))
    except Exception as e:
        logging.error(f"Error removing premium: {e}")
        await message.answer(f"❌ خطا: {e}")


@router.callback_query(F.data == "check_user_info")
async def start_check_user_info(callback: types.CallbackQuery, state: FSMContext):
    """Start the process of checking user information."""
    if callback.from_user.id != DEVELOPER_ID:
        await callback.answer("❌ Access denied", show_alert=True)
        return
        
    lang = await database.get_user_language(callback.from_user.id) or 'en'
    await state.set_state(Form.waiting_for_user_id_info)
    
    await callback.message.edit_text(get_text('enter_user_id_for_premium', lang))


@router.message(Form.waiting_for_user_id_info, F.text)
async def process_user_info_check(message: types.Message, state: FSMContext):
    """Process user information check."""
    if message.from_user.id != DEVELOPER_ID:
        return
        
    lang = await database.get_user_language(message.from_user.id) or 'en'
    
    try:
        target_user_id = int(message.text.strip())
        
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
                await message.answer(get_text('user_not_found', lang))
                return
                
            # Get user channels count
            cursor = await db.execute('SELECT COUNT(*) FROM channels WHERE user_id = ?', (target_user_id,))
            channels_count = (await cursor.fetchone())[0]
            
        user_id, lang_code, is_premium, premium_until, created_at, posts_month, total_posts = user_data
        
        info_text = f"""👤 اطلاعات کاربر:

🆔 شناسه کاربر: {user_id}
🌐 زبان: {lang_code or 'تنظیم نشده'}
💎 پریمیوم: {'بله' if is_premium else 'خیر'}
📅 پریمیوم تا: {premium_until or 'ندارد'}
📊 پست‌های این ماه: {posts_month or 0}
📈 کل پست‌ها: {total_posts or 0}
📢 تعداد کانال‌ها: {channels_count}
🗓️ تاریخ عضویت: {created_at or 'نامشخص'}"""

        await message.answer(info_text)
        await state.clear()
        
    except ValueError:
        await message.answer(get_text('invalid_user_id', lang))
    except Exception as e:
        logging.error(f"Error showing user info: {e}")
        await message.answer(f"❌ خطا: {e}")


@router.callback_query(F.data == "premium_stats")
async def show_premium_stats(callback: types.CallbackQuery):
    """Show premium statistics."""
    if callback.from_user.id != DEVELOPER_ID:
        await callback.answer("❌ Access denied", show_alert=True)
        return
        
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
            
        stats_text = f"""📊 آمار ربات:

👥 کل کاربران: {total_users}
💎 کاربران پریمیوم: {premium_users}
🆓 کاربران رایگان: {total_users - premium_users}
📢 کل کانال‌ها: {total_channels}
📨 کل پست‌های ارسالی: {total_posts}
📅 پست‌های این ماه: {posts_this_month}

💰 نرخ تبدیل پریمیوم: {(premium_users/total_users*100):.1f}%"""

        await callback.message.edit_text(stats_text)
        
    except Exception as e:
        logging.error(f"Error showing premium stats: {e}")
        await callback.message.edit_text(f"❌ خطا: {e}")


@router.callback_query(F.data == "back_to_premium_menu")
async def back_to_premium_menu(callback: types.CallbackQuery, state: FSMContext):
    """Go back to premium management menu."""
    if callback.from_user.id != DEVELOPER_ID:
        await callback.answer("❌ Access denied", show_alert=True)
        return
        
    lang = await database.get_user_language(callback.from_user.id) or 'en'
    await state.clear()
    
    await callback.message.edit_text(
        get_text('premium_management_menu', lang),
        reply_markup=get_premium_management_keyboard(lang)
    )


# --- User Management Menu ---

@router.message(F.text.in_([get_text('developer_manage_users_button', 'fa'), get_text('developer_manage_users_button', 'en')]))
async def show_user_management_menu(message: types.Message):
    """Shows user management menu for developer."""
    user_id = message.from_user.id
    if user_id != DEVELOPER_ID:
        return
        
    lang = await database.get_user_language(user_id) or 'en'
    
    await message.answer(
        "👥 منوی مدیریت کاربران\n\nلطفا یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=get_user_management_keyboard(lang)
    )


# --- Statistics Menu ---

@router.message(F.text.in_([get_text('developer_stats_button', 'fa'), get_text('developer_stats_button', 'en')]))
async def show_stats_menu(message: types.Message):
    """Shows bot statistics for developer."""
    user_id = message.from_user.id
    if user_id != DEVELOPER_ID:
        return
        
    await show_stats_command(message)


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
            
        stats_text = f"""📊 آمار کامل ربات:

👥 کل کاربران: {total_users}
💎 کاربران پریمیوم: {premium_users}
🆓 کاربران رایگان: {total_users - premium_users}
📢 کل کانال‌ها: {total_channels}
📨 کل پست‌های ارسالی: {total_posts}
📅 پست‌های این ماه: {posts_this_month}

📈 میانگین کانال به ازای هر کاربر: {(total_channels/total_users):.1f}
💰 نرخ تبدیل پریمیوم: {(premium_users/total_users*100):.1f}%
📊 میانگین پست به ازای هر کاربر: {(total_posts/total_users):.1f}"""

        await message.answer(stats_text)
        
    except Exception as e:
        logging.error(f"Error showing stats: {e}")
        await message.answer(f"❌ خطا: {e}")


# --- Legacy command support (for backward compatibility) ---

@router.message(F.from_user.id == DEVELOPER_ID, F.text.startswith("/setpremium"))
async def set_premium_command(message: types.Message):
    """Developer command to set user as premium. Usage: /setpremium USER_ID [DAYS]"""
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("استفاده: /setpremium USER_ID [DAYS]\nمثال: /setpremium 123456789 30")
            return
            
        target_user_id = int(parts[1])
        days = int(parts[2]) if len(parts) > 2 else 365  # Default 1 year
        
        from datetime import datetime, timedelta
        premium_until = (datetime.now() + timedelta(days=days)).isoformat()
        
        await database.set_user_premium(target_user_id, premium_until)
        await message.answer(f"✅ کاربر {target_user_id} به مدت {days} روز پریمیوم شد.")
        
        # Notify the user
        try:
            user_lang = await database.get_user_language(target_user_id) or 'en'
            notification = get_text('premium_notification_granted', user_lang)
            await message.bot.send_message(target_user_id, notification)
        except Exception:
            pass  # User might have blocked the bot
            
    except (ValueError, IndexError):
        await message.answer("فرمت نامعتبر. استفاده: /setpremium USER_ID [DAYS]")
    except Exception as e:
        logging.error(f"Error setting premium: {e}")
        await message.answer(f"❌ خطا: {e}")


@router.message(F.from_user.id == DEVELOPER_ID, F.text.startswith("/removepremium"))
async def remove_premium_command(message: types.Message):
    """Developer command to remove premium from user. Usage: /removepremium USER_ID"""
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("استفاده: /removepremium USER_ID")
            return
            
        target_user_id = int(parts[1])
        
        # Set premium to 0 and clear premium_until
        await database.set_user_premium(target_user_id, None)
        # Also update is_premium to 0
        import aiosqlite
        async with aiosqlite.connect(database.DB_NAME) as db:
            await db.execute('UPDATE users SET is_premium = 0 WHERE user_id = ?', (target_user_id,))
            await db.commit()
            
        await message.answer(f"✅ پریمیوم کاربر {target_user_id} حذف شد.")
        
        # Notify the user
        try:
            user_lang = await database.get_user_language(target_user_id) or 'en'
            notification = get_text('premium_notification_removed', user_lang)
            await message.bot.send_message(target_user_id, notification)
        except Exception:
            pass  # User might have blocked the bot
            
    except (ValueError, IndexError):
        await message.answer("فرمت نامعتبر. استفاده: /removepremium USER_ID")
    except Exception as e:
        logging.error(f"Error removing premium: {e}")
        await message.answer(f"❌ خطا: {e}")


@router.message(F.from_user.id == DEVELOPER_ID, F.text.startswith("/userinfo"))
async def show_user_info_command(message: types.Message):
    """Shows information about a specific user."""
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("استفاده: /userinfo USER_ID")
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
                await message.answer(f"❌ کاربر {target_user_id} یافت نشد.")
                return
                
            # Get user channels count
            cursor = await db.execute('SELECT COUNT(*) FROM channels WHERE user_id = ?', (target_user_id,))
            channels_count = (await cursor.fetchone())[0]
            
        user_id, lang_code, is_premium, premium_until, created_at, posts_month, total_posts = user_data
        
        info_text = f"""👤 اطلاعات کاربر:

🆔 شناسه کاربر: {user_id}
🌐 زبان: {lang_code or 'تنظیم نشده'}
💎 پریمیوم: {'بله' if is_premium else 'خیر'}
📅 پریمیوم تا: {premium_until or 'ندارد'}
📊 پست‌های این ماه: {posts_month or 0}
📈 کل پست‌ها: {total_posts or 0}
📢 تعداد کانال‌ها: {channels_count}
🗓️ تاریخ عضویت: {created_at or 'نامشخص'}"""

        await message.answer(info_text)
        
    except (ValueError, IndexError):
        await message.answer("فرمت نامعتبر. استفاده: /userinfo USER_ID")
    except Exception as e:
        logging.error(f"Error showing user info: {e}")
        await message.answer(f"❌ خطا: {e}")