import logging
from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from datetime import timedelta

import database
from texts import get_text
from states import Form
from keyboards import (
    get_channel_premium_keyboard, 
    get_premium_duration_purchase_keyboard,
    get_payment_requests_keyboard,
    get_payment_approval_keyboard
)
from config import PAYMENT_CARD_NUMBER, PAYMENT_CARD_HOLDER, PAYMENT_PRICES, DEVELOPER_ID

router = Router()

# --- Channel Premium Purchase Flow ---

@router.message(F.text.in_([get_text('upgrade_premium_button', 'fa'), get_text('upgrade_premium_button', 'en')]))
async def show_channel_premium_info(message: types.Message, bot: Bot):
    """Shows channel premium information and selection."""
    user_id = message.from_user.id
    lang = await database.get_user_language(user_id) or 'en'
    
    try:
        # Get user channels with premium status
        channels_info = await database.get_user_channels_with_premium_status(user_id)
        
        if not channels_info:
            await message.answer(get_text('error_no_channels_for_broadcast', lang))
            return
        
        # Add channel titles and usernames
        for channel_info in channels_info:
            try:
                chat = await bot.get_chat(channel_info['channel_id'])
                channel_info['title'] = chat.title
                # Add username if available
                if hasattr(chat, 'username') and chat.username:
                    channel_info['username'] = f"@{chat.username}"
                else:
                    channel_info['username'] = f"ID: {channel_info['channel_id']}"
            except Exception as e:
                logging.error(f"Error getting chat info: {e}")
                channel_info['title'] = f"کانال {channel_info['channel_id']}"
                channel_info['username'] = f"ID: {channel_info['channel_id']}"
        
        text = get_text('channel_premium_info', lang)
        await message.answer(
            text,
            reply_markup=get_channel_premium_keyboard(lang, channels_info)
        )
        
    except Exception as e:
        logging.error(f"Error showing channel premium info: {e}")
        await message.answer(get_text('error_occurred', lang))

@router.callback_query(F.data.startswith("upgrade_channel_"))
async def select_channel_for_premium(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Handle channel selection for premium upgrade."""
    user_id = callback.from_user.id
    lang = await database.get_user_language(user_id) or 'en'
    
    try:
        channel_id = int(callback.data.split("_")[2])
        
        # Check if channel is already premium
        if await database.is_channel_premium(channel_id, user_id):
            await callback.answer(get_text('channel_already_premium', lang), show_alert=True)
            return
        
        # Get channel info with username
        chat = await bot.get_chat(channel_id)
        channel_title = chat.title
        if hasattr(chat, 'username') and chat.username:
            channel_identifier = f"@{chat.username}"
        else:
            channel_identifier = f"ID: {channel_id}"
        
        # Store channel info in state
        await state.update_data(
            selected_channel_id=channel_id,
            selected_channel_title=channel_title,
            selected_channel_identifier=channel_identifier
        )
        
        await callback.message.edit_text(
            get_text('select_premium_duration_purchase', lang),
            reply_markup=get_premium_duration_purchase_keyboard(lang)
        )
        
    except Exception as e:
        logging.error(f"Error selecting channel for premium: {e}")
        await callback.answer(get_text('error_occurred', lang), show_alert=True)

@router.callback_query(F.data.startswith("buy_premium_"))
async def process_premium_purchase(callback: types.CallbackQuery, state: FSMContext):
    """Process premium purchase request."""
    user_id = callback.from_user.id
    lang = await database.get_user_language(user_id) or 'en'
    
    try:
        duration_months = int(callback.data.split("_")[2])
        amount = PAYMENT_PRICES.get(duration_months, 0)
        
        if amount == 0:
            await callback.answer("❌ مدت زمان نامعتبر", show_alert=True)
            return
        
        data = await state.get_data()
        channel_id = data.get('selected_channel_id')
        channel_title = data.get('selected_channel_title')
        channel_identifier = data.get('selected_channel_identifier', f"ID: {channel_id}")
        
        if not channel_id:
            await callback.answer("❌ خطا در انتخاب کانال", show_alert=True)
            return
        
        # Create payment request with channel identifier
        request_id = await database.create_payment_request(
            user_id, channel_id, f"{channel_title} ({channel_identifier})", duration_months, amount
        )
        
        # Store request ID in state
        await state.update_data(payment_request_id=request_id)
        await state.set_state(Form.waiting_for_payment_receipt)
        
        # Send payment info with channel identifier
        payment_text = get_text('payment_info', lang).format(
            card_number=PAYMENT_CARD_NUMBER,
            card_holder=PAYMENT_CARD_HOLDER,
            amount=amount,
            duration=duration_months,
            channel_title=f"{channel_title} ({channel_identifier})"
        )
        
        await callback.message.edit_text(payment_text)
        await callback.message.answer(get_text('waiting_for_receipt', lang))
        
    except Exception as e:
        logging.error(f"Error processing premium purchase: {e}")
        await callback.answer(get_text('error_occurred', lang), show_alert=True)

@router.callback_query(F.data == "back_to_channel_selection")
async def back_to_channel_selection(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Go back to channel selection."""
    await state.clear()
    await show_channel_premium_info(callback.message, bot)

@router.message(Form.waiting_for_payment_receipt, F.photo)
async def process_payment_receipt(message: types.Message, state: FSMContext, bot: Bot):
    """Process payment receipt photo."""
    user_id = message.from_user.id
    lang = await database.get_user_language(user_id) or 'en'
    
    try:
        data = await state.get_data()
        request_id = data.get('payment_request_id')
        
        if not request_id:
            await message.answer("❌ خطا در پردازش درخواست")
            return
        
        # Update payment request with receipt
        await database.update_payment_receipt(request_id, message.message_id)
        
        # Get payment request details
        payment_request = await database.get_payment_request(request_id)
        
        if payment_request:
            # Send receipt to developer
            await send_receipt_to_developer(bot, payment_request, message)
            
            # Notify user
            await message.answer(get_text('receipt_received', lang))
            
        await state.clear()
        
    except Exception as e:
        logging.error(f"Error processing payment receipt: {e}")
        await message.answer(get_text('error_occurred', lang))

@router.message(Form.waiting_for_payment_receipt)
async def invalid_receipt_handler(message: types.Message, state: FSMContext):
    """Handle invalid receipt (non-photo)."""
    lang = await database.get_user_language(message.from_user.id) or 'en'
    await message.answer(get_text('invalid_receipt', lang))

async def send_receipt_to_developer(bot: Bot, payment_request: dict, receipt_message: types.Message):
    """Send payment receipt to developer for approval."""
    try:
        if not DEVELOPER_ID or DEVELOPER_ID == 0:
            return
        
        # Format payment details with Persian date
        created_persian = database.format_persian_date(payment_request['created_at'])
        
        details_text = f"""💳 درخواست پرداخت جدید

👤 کاربر: {payment_request['user_id']}
📺 کانال: {payment_request['channel_title']}
💰 مبلغ: {payment_request['amount']:,} تومان
📅 مدت: {payment_request['duration_months']} ماه
🕐 تاریخ درخواست: {created_persian}

📸 رسید پرداخت:"""
        
        # Send details
        await bot.send_message(DEVELOPER_ID, details_text)
        
        # Forward receipt photo
        await bot.forward_message(
            chat_id=DEVELOPER_ID,
            from_chat_id=receipt_message.chat.id,
            message_id=receipt_message.message_id
        )
        
        # Send approval keyboard
        await bot.send_message(
            DEVELOPER_ID,
            "👆 رسید پرداخت بالا",
            reply_markup=get_payment_approval_keyboard('fa', payment_request['id'])
        )
        
    except Exception as e:
        logging.error(f"Error sending receipt to developer: {e}")

# --- Developer Payment Management ---

@router.message(F.text.in_([get_text('manage_payments_button', 'fa'), get_text('manage_payments_button', 'en')]))
async def show_payment_requests(message: types.Message):
    """Show pending payment requests for developer."""
    user_id = message.from_user.id
    if user_id != DEVELOPER_ID:
        return
    
    lang = await database.get_user_language(user_id) or 'en'
    
    try:
        requests = await database.get_pending_payment_requests()
        
        if not requests:
            await message.answer(get_text('no_payment_requests', lang))
            return
        
        await message.answer(
            get_text('payment_requests_title', lang),
            reply_markup=get_payment_requests_keyboard(lang, requests)
        )
        
    except Exception as e:
        logging.error(f"Error showing payment requests: {e}")
        await message.answer(get_text('error_occurred', lang))

@router.callback_query(F.data.startswith("view_payment_"))
async def view_payment_details(callback: types.CallbackQuery):
    """View payment request details."""
    if callback.from_user.id != DEVELOPER_ID:
        await callback.answer("❌ Access denied", show_alert=True)
        return
    
    try:
        request_id = int(callback.data.split("_")[2])
        payment_request = await database.get_payment_request(request_id)
        
        if not payment_request:
            await callback.answer("❌ درخواست یافت نشد", show_alert=True)
            return
        
        # Format with Persian date
        created_persian = database.format_persian_date(payment_request['created_at'])
        
        details_text = f"""💳 جزئیات درخواست پرداخت

👤 کاربر: {payment_request['user_id']}
📺 کانال: {payment_request['channel_title']}
💰 مبلغ: {payment_request['amount']:,} تومان
📅 مدت: {payment_request['duration_months']} ماه
🕐 تاریخ: {created_persian}

📸 رسید پرداخت ارسال شده است."""
        
        await callback.message.edit_text(
            details_text,
            reply_markup=get_payment_approval_keyboard('fa', request_id)
        )
        
    except Exception as e:
        logging.error(f"Error viewing payment details: {e}")
        await callback.answer("❌ خطا در نمایش جزئیات", show_alert=True)

@router.callback_query(F.data.startswith("approve_payment_"))
async def approve_payment(callback: types.CallbackQuery, bot: Bot):
    """Approve payment request."""
    if callback.from_user.id != DEVELOPER_ID:
        await callback.answer("❌ Access denied", show_alert=True)
        return
    
    try:
        request_id = int(callback.data.split("_")[2])
        payment_request = await database.get_payment_request(request_id)
        
        if not payment_request:
            await callback.answer("❌ درخواست یافت نشد", show_alert=True)
            return
        
        # Approve payment and set channel as premium
        success = await database.approve_payment_request(request_id)
        
        if success:
            # Calculate expiry date for display
            tehran_time = database.get_tehran_time()
            expiry_date = tehran_time + timedelta(days=payment_request['duration_months'] * 30)
            expiry_persian = database.format_persian_date(expiry_date)
            
            await callback.message.edit_text(f"✅ پرداخت تایید شد و کانال پریمیوم شد.\n📅 انقضا: {expiry_persian}")
            
            # Notify user with Persian expiry date
            user_lang = await database.get_user_language(payment_request['user_id']) or 'en'
            notification = f"🎉 پرداخت شما تایید شد!\n\n💎 کانال {payment_request['channel_title']} به مدت {payment_request['duration_months']} ماه پریمیوم شد.\n📅 انقضا: {expiry_persian}\n\n✨ حالا می‌توانید پست‌های نامحدود ارسال کنید!"
            
            try:
                await bot.send_message(payment_request['user_id'], notification)
            except Exception:
                pass  # User might have blocked the bot
        else:
            await callback.answer("❌ خطا در تایید پرداخت", show_alert=True)
        
    except Exception as e:
        logging.error(f"Error approving payment: {e}")
        await callback.answer("❌ خطا در تایید پرداخت", show_alert=True)

@router.callback_query(F.data.startswith("reject_payment_"))
async def reject_payment(callback: types.CallbackQuery, bot: Bot):
    """Reject payment request."""
    if callback.from_user.id != DEVELOPER_ID:
        await callback.answer("❌ Access denied", show_alert=True)
        return
    
    try:
        request_id = int(callback.data.split("_")[2])
        payment_request = await database.get_payment_request(request_id)
        
        if not payment_request:
            await callback.answer("❌ درخواست یافت نشد", show_alert=True)
            return
        
        # Reject payment
        await database.reject_payment_request(request_id)
        
        await callback.message.edit_text("❌ پرداخت رد شد.")
        
        # Notify user
        user_lang = await database.get_user_language(payment_request['user_id']) or 'en'
        notification = get_text('payment_rejected', user_lang)
        
        try:
            await bot.send_message(payment_request['user_id'], notification)
        except Exception:
            pass  # User might have blocked the bot
        
    except Exception as e:
        logging.error(f"Error rejecting payment: {e}")
        await callback.answer("❌ خطا در رد پرداخت", show_alert=True)

@router.callback_query(F.data == "back_to_payments")
async def back_to_payments(callback: types.CallbackQuery):
    """Go back to payment requests list."""
    if callback.from_user.id != DEVELOPER_ID:
        await callback.answer("❌ Access denied", show_alert=True)
        return
    
    try:
        requests = await database.get_pending_payment_requests()
        
        await callback.message.edit_text(
            get_text('payment_requests_title', 'fa'),
            reply_markup=get_payment_requests_keyboard('fa', requests)
        )
        
    except Exception as e:
        logging.error(f"Error going back to payments: {e}")
        await callback.answer("❌ خطا", show_alert=True)

@router.callback_query(F.data == "no_requests")
async def no_requests_handler(callback: types.CallbackQuery):
    """Handle no requests callback."""
    await callback.answer()