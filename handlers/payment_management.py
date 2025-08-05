import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

import database
from texts import get_text
from config import DEVELOPER_ID

router = Router()

@router.message(F.text.in_([get_text('manage_payments_button', 'fa'), get_text('manage_payments_button', 'en')]))
async def show_all_payment_requests(message: types.Message):
    """Show all payment requests with Persian dates for developer."""
    user_id = message.from_user.id
    if user_id != DEVELOPER_ID:
        return
    
    lang = await database.get_user_language(user_id) or 'en'
    
    try:
        # Get all payment requests (not just pending)
        all_requests = await database.get_all_payment_requests()
        
        if not all_requests:
            await message.answer("هیچ درخواست پرداختی وجود ندارد.")
            return
        
        # Group by status
        pending_requests = [r for r in all_requests if r['status'] == 'pending']
        approved_requests = [r for r in all_requests if r['status'] == 'approved']
        rejected_requests = [r for r in all_requests if r['status'] == 'rejected']
        
        text = "💳 **گزارش کامل پرداخت‌ها**\n\n"
        
        # Pending requests
        if pending_requests:
            text += "⏳ **درخواست‌های در انتظار:**\n"
            for req in pending_requests:
                created_date = database.format_persian_date(req['created_at'])
                text += f"├── {req['channel_title']}\n"
                text += f"│   💰 {req['amount']:,} تومان ({req['duration_months']} ماه)\n"
                text += f"│   📅 {created_date}\n"
                text += f"│   👤 کاربر: {req['user_id']}\n\n"
        
        # Approved requests
        if approved_requests:
            text += "✅ **پرداخت‌های تایید شده:**\n"
            for req in approved_requests:
                created_date = database.format_persian_date(req['created_at'])
                processed_date = database.format_persian_date(req['processed_at']) if req['processed_at'] else 'نامشخص'
                
                # Get expiry date
                expiry_text = "نامشخص"
                if req.get('premium_until'):
                    expiry_text = database.format_persian_date(req['premium_until'])
                
                text += f"├── {req['channel_title']}\n"
                text += f"│   💰 {req['amount']:,} تومان ({req['duration_months']} ماه)\n"
                text += f"│   📅 خرید: {created_date}\n"
                text += f"│   ✅ تایید: {processed_date}\n"
                text += f"│   ⏰ انقضا: {expiry_text}\n"
                text += f"│   👤 کاربر: {req['user_id']}\n\n"
        
        # Rejected requests
        if rejected_requests:
            text += "❌ **پرداخت‌های رد شده:**\n"
            for req in rejected_requests:
                created_date = database.format_persian_date(req['created_at'])
                processed_date = database.format_persian_date(req['processed_at']) if req['processed_at'] else 'نامشخص'
                text += f"├── {req['channel_title']}\n"
                text += f"│   💰 {req['amount']:,} تومان ({req['duration_months']} ماه)\n"
                text += f"│   📅 درخواست: {created_date}\n"
                text += f"│   ❌ رد: {processed_date}\n"
                text += f"│   👤 کاربر: {req['user_id']}\n\n"
        
        # Summary
        total_revenue = sum(r['amount'] for r in approved_requests)
        text += f"📊 **خلاصه:**\n"
        text += f"├── کل درخواست‌ها: {len(all_requests)}\n"
        text += f"├── در انتظار: {len(pending_requests)}\n"
        text += f"├── تایید شده: {len(approved_requests)}\n"
        text += f"├── رد شده: {len(rejected_requests)}\n"
        text += f"└── کل درآمد: {total_revenue:,} تومان"
        
        # Split long messages
        if len(text) > 4000:
            # Send in parts
            parts = text.split('\n\n')
            current_part = ""
            
            for part in parts:
                if len(current_part + part) > 3500:
                    if current_part:
                        await message.answer(current_part, parse_mode="Markdown")
                        current_part = part + "\n\n"
                    else:
                        await message.answer(part, parse_mode="Markdown")
                else:
                    current_part += part + "\n\n"
            
            if current_part:
                await message.answer(current_part, parse_mode="Markdown")
        else:
            await message.answer(text, parse_mode="Markdown")
        
    except Exception as e:
        logging.error(f"Error showing payment requests: {e}")
        await message.answer(f"❌ خطا: {e}")

@router.message(F.from_user.id == DEVELOPER_ID, F.text.startswith("/payments"))
async def show_payment_stats_command(message: types.Message):
    """Show payment statistics command."""
    try:
        all_requests = await database.get_all_payment_requests()
        
        if not all_requests:
            await message.answer("هیچ درخواست پرداختی وجود ندارد.")
            return
        
        # Calculate statistics
        total_requests = len(all_requests)
        pending_count = len([r for r in all_requests if r['status'] == 'pending'])
        approved_count = len([r for r in all_requests if r['status'] == 'approved'])
        rejected_count = len([r for r in all_requests if r['status'] == 'rejected'])
        
        total_revenue = sum(r['amount'] for r in all_requests if r['status'] == 'approved')
        pending_revenue = sum(r['amount'] for r in all_requests if r['status'] == 'pending')
        
        # Monthly statistics
        from datetime import datetime
        current_month = database.get_tehran_time().strftime('%Y-%m')
        monthly_requests = [r for r in all_requests if r['created_at'].startswith(current_month)]
        monthly_revenue = sum(r['amount'] for r in monthly_requests if r['status'] == 'approved')
        
        stats_text = f"""💳 آمار پرداخت‌ها:

📊 **کل آمار:**
├── کل درخواست‌ها: {total_requests}
├── در انتظار: {pending_count}
├── تایید شده: {approved_count}
├── رد شده: {rejected_count}

💰 **درآمد:**
├── کل درآمد: {total_revenue:,} تومان
├── در انتظار: {pending_revenue:,} تومان
├── درآمد این ماه: {monthly_revenue:,} تومان

📈 **نرخ‌ها:**
├── نرخ تایید: {(approved_count/total_requests*100):.1f}%
├── نرخ رد: {(rejected_count/total_requests*100):.1f}%
└── میانگین درآمد/درخواست: {(total_revenue/approved_count if approved_count > 0 else 0):,.0f} تومان"""

        await message.answer(stats_text)
        
    except Exception as e:
        logging.error(f"Error showing payment stats: {e}")
        await message.answer(f"❌ خطا: {e}")

@router.message(F.from_user.id == DEVELOPER_ID, F.text.startswith("/revenue"))
async def show_revenue_details(message: types.Message):
    """Show detailed revenue breakdown."""
    try:
        all_requests = await database.get_all_payment_requests()
        approved_requests = [r for r in all_requests if r['status'] == 'approved']
        
        if not approved_requests:
            await message.answer("هیچ پرداخت تایید شده‌ای وجود ندارد.")
            return
        
        # Group by month
        monthly_revenue = {}
        for req in approved_requests:
            try:
                month = req['processed_at'][:7] if req['processed_at'] else req['created_at'][:7]  # YYYY-MM
                if month not in monthly_revenue:
                    monthly_revenue[month] = {'count': 0, 'amount': 0}
                monthly_revenue[month]['count'] += 1
                monthly_revenue[month]['amount'] += req['amount']
            except:
                pass
        
        text = "💰 **گزارش درآمد ماهانه:**\n\n"
        
        # Sort by month (newest first)
        sorted_months = sorted(monthly_revenue.keys(), reverse=True)
        
        for month in sorted_months:
            data = monthly_revenue[month]
            # Convert to Persian month name if possible
            try:
                year, month_num = month.split('-')
                persian_months = [
                    'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
                    'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
                ]
                # This is a simple approximation - for exact conversion you'd need jdatetime
                month_name = f"{year}/{month_num}"
            except:
                month_name = month
            
            text += f"📅 **{month_name}:**\n"
            text += f"├── تعداد: {data['count']} پرداخت\n"
            text += f"└── مبلغ: {data['amount']:,} تومان\n\n"
        
        total_revenue = sum(data['amount'] for data in monthly_revenue.values())
        total_count = sum(data['count'] for data in monthly_revenue.values())
        
        text += f"📊 **کل:**\n"
        text += f"├── {total_count} پرداخت\n"
        text += f"└── {total_revenue:,} تومان"
        
        await message.answer(text, parse_mode="Markdown")
        
    except Exception as e:
        logging.error(f"Error showing revenue details: {e}")
        await message.answer(f"❌ خطا: {e}")