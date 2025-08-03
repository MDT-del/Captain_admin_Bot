import logging
import uuid
import jdatetime
import datetime
from pytz import timezone
from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import database
from texts import get_text
from states import Form
from keyboards import get_post_action_keyboard, get_channel_selection_keyboard, get_caption_choice_keyboard
from utils.persian_calendar import create_persian_calendar, CALENDAR_CALLBACK_PREFIX, PREV_MONTH_CALLBACK, NEXT_MONTH_CALLBACK, DAY_CALLBACK

router = Router()

# --- 1. Content Entry Point ---

@router.message(F.content_type.in_({'text', 'photo', 'video', 'document', 'audio', 'voice'}))
async def content_entry_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await database.get_user_language(user_id) or 'en'

    # Check if user has registered channels
    if not await database.get_user_channels(user_id):
        await message.answer(get_text('error_no_channels_for_broadcast', lang))
        return

    # Check post limit for non-premium users
    can_send, remaining = await database.can_user_send_post(user_id)
    if not can_send:
        from config import FREE_USER_POST_LIMIT
        await message.answer(get_text('post_limit_reached', lang).format(limit=FREE_USER_POST_LIMIT))
        return

    await state.set_data({
        'post_message_id': message.message_id,
        'post_chat_id': message.chat.id,
        'selected_channels': []
    })

    await message.answer(get_text('post_action_menu_title', lang), reply_markup=get_post_action_keyboard(lang))

# --- 2. Broadcasting & Scheduling Workflow ---

@router.callback_query(F.data == "cancel_broadcast")
async def cancel_broadcast_handler(callback: types.CallbackQuery, state: FSMContext):
    lang = await database.get_user_language(callback.from_user.id) or 'en'
    await state.clear()
    await callback.message.edit_text(get_text('operation_cancelled', lang))

@router.callback_query(F.data == "send_now")
async def send_now_handler(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await state.update_data(is_scheduled=False)
    await start_channel_selection(callback, state, bot)

@router.callback_query(F.data == "send_scheduled")
async def send_scheduled_handler(callback: types.CallbackQuery, state: FSMContext):
    lang = await database.get_user_language(callback.from_user.id) or 'en'
    await state.update_data(is_scheduled=True)
    await callback.message.edit_text(
        get_text('prompt_for_schedule_date', lang),
        reply_markup=await create_persian_calendar()
    )

# --- 3. Calendar Handlers ---

@router.callback_query(F.data.startswith(f"{CALENDAR_CALLBACK_PREFIX}_"))
async def calendar_process(callback: types.CallbackQuery, state: FSMContext):
    lang = await database.get_user_language(callback.from_user.id) or 'en'
    data = callback.data.split('_')
    action = data[1]

    if action == "ignore":
        await callback.answer()
        return

    if action in ["prev", "next"]:
        year, month = int(data[2]), int(data[3])
        await callback.message.edit_reply_markup(reply_markup=await create_persian_calendar(year, month))
        await callback.answer()
        return

    if action == "day":
        year, month, day = int(data[2]), int(data[3]), int(data[4])
        selected_date = jdatetime.date(year, month, day)
        await state.update_data(scheduled_date=selected_date.strftime('%Y-%m-%d'))
        await state.set_state(Form.selecting_schedule_time)
        await callback.message.edit_text(
            get_text('prompt_for_schedule_time', lang).format(date=selected_date.strftime('%Y/%m/%d'))
        )
        await callback.answer()

# --- 4. Time, Channel, and Caption Handlers ---

@router.message(Form.selecting_schedule_time, F.text)
async def process_schedule_time(message: types.Message, state: FSMContext, bot: Bot):
    lang = await database.get_user_language(message.from_user.id) or 'en'
    try:
        hour, minute = map(int, message.text.split(':'))
        data = await state.get_data()
        jalali_date = jdatetime.datetime.strptime(data['scheduled_date'], '%Y-%m-%d').date()

        tehran_tz = timezone('Asia/Tehran')
        local_dt = tehran_tz.localize(datetime.datetime(
            year=jalali_date.togregorian().year,
            month=jalali_date.togregorian().month,
            day=jalali_date.togregorian().day,
            hour=hour,
            minute=minute
        ))
        utc_dt = local_dt.astimezone(datetime.timezone.utc)

        if utc_dt < datetime.datetime.now(datetime.timezone.utc):
             await message.answer("زمان انتخاب شده در گذشته است. لطفا زمان دیگری انتخاب کنید.")
             return

        await state.update_data(scheduled_datetime_utc=utc_dt)
        await state.set_state(None)

        # Re-trigger the channel selection process now that time is set
        # We create a mock callback object to reuse the handler
        mock_callback = types.CallbackQuery(id="mock", from_user=message.from_user, chat_instance="", message=message)
        await start_channel_selection(mock_callback, state, bot)
        await message.delete() # clean up the time message

    except (ValueError, IndexError):
        await message.answer(get_text('error_invalid_time_format', lang))

async def start_channel_selection(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    # This function is now a reusable entry point for channel selection
    user_id = callback.from_user.id
    lang = await database.get_user_language(user_id) or 'en'
    db_channels = await database.get_user_channels(user_id)
    all_channels_info = [{'id': c[0], 'title': (await bot.get_chat(c[0])).title} for c in db_channels]

    await state.update_data(all_channels=all_channels_info)
    await state.set_state(Form.selecting_channels)

    # Use edit_text if coming from a callback, answer if from a message
    if callback.message:
        await callback.message.edit_text(
            get_text('select_channels_prompt', lang),
            reply_markup=get_channel_selection_keyboard(lang, all_channels_info, [])
        )
    else:
         await bot.send_message(user_id, get_text('select_channels_prompt', lang),
                                reply_markup=get_channel_selection_keyboard(lang, all_channels_info, []))


@router.callback_query(Form.selecting_channels, F.data.startswith("select_channel_"))
async def select_channel_handler(callback: types.CallbackQuery, state: FSMContext):
    channel_id = int(callback.data.split("_")[2])
    lang = await database.get_user_language(callback.from_user.id) or 'en'
    data = await state.get_data()
    selected = data.get('selected_channels', [])
    if channel_id in selected:
        selected.remove(channel_id)
    else:
        selected.append(channel_id)
    await state.update_data(selected_channels=selected)
    await callback.message.edit_reply_markup(reply_markup=get_channel_selection_keyboard(lang, data['all_channels'], selected))

@router.callback_query(Form.selecting_channels, F.data == "confirm_channels")
async def confirm_channels_handler(callback: types.CallbackQuery, state: FSMContext):
    lang = await database.get_user_language(callback.from_user.id) or 'en'
    await state.set_state(None)
    await callback.message.edit_text(get_text('ask_for_caption_prompt', lang), reply_markup=get_caption_choice_keyboard(lang))

@router.callback_query(F.data.startswith("add_caption_"))
async def caption_choice_handler(callback: types.CallbackQuery, state: FSMContext, scheduler: AsyncIOScheduler, bot: Bot):
    choice = callback.data.split("_")[2]
    lang = await database.get_user_language(callback.from_user.id) or 'en'
    if choice == "yes":
        await state.set_state(Form.waiting_for_caption)
        await callback.message.edit_text(get_text('prompt_for_caption', lang))
    else:
        await callback.message.edit_text("در حال پردازش...")
        await send_final_post(callback.from_user.id, state, bot, scheduler)

@router.message(Form.waiting_for_caption, F.text)
async def process_caption_handler(message: types.Message, state: FSMContext, bot: Bot, scheduler: AsyncIOScheduler):
    await state.update_data(caption=message.text)
    await message.answer("کپشن دریافت شد. در حال پردازش...")
    await send_final_post(message.from_user.id, state, bot, scheduler)

# --- 5. Final Sending/Scheduling Logic ---

async def send_final_post(user_id: int, state: FSMContext, bot: Bot, scheduler: AsyncIOScheduler):
    data = await state.get_data()
    lang = await database.get_user_language(user_id) or 'en'

    is_scheduled = data.get('is_scheduled', False)
    post_message_id = data['post_message_id']
    post_chat_id = data['post_chat_id']
    target_channels = data['selected_channels']
    caption = data.get('caption')
    footer = await database.get_user_footer(user_id)

    final_caption = f"{caption}\n\n{footer}" if caption and footer else caption or footer or ""

    if is_scheduled:
        scheduled_time_utc = data['scheduled_datetime_utc']
        for channel_id in target_channels:
            job_id = str(uuid.uuid4())
            scheduler.add_job(
                "utils.scheduler.send_scheduled_post",
                trigger='date',
                run_date=scheduled_time_utc,
                args=[job_id, bot],
                id=job_id,
                misfire_grace_time=3600 # Allow to run up to 1h late
            )
            await database.add_scheduled_post(job_id, user_id, post_chat_id, post_message_id, channel_id, final_caption, scheduled_time_utc.isoformat())

        jalali_time = jdatetime.datetime.fromgregorian(datetime=data['scheduled_datetime_utc'].astimezone(timezone('Asia/Tehran')))
        await bot.send_message(user_id, get_text('schedule_success', lang).format(
            date=jalali_time.strftime('%Y/%m/%d'), time=jalali_time.strftime('%H:%M')))
    else:
        sent_count = 0
        for channel_id in target_channels:
            try:
                await bot.copy_message(chat_id=channel_id, from_chat_id=post_chat_id, message_id=post_message_id, caption=final_caption or None, parse_mode="HTML")
                sent_count += 1
            except Exception as e:
                logging.error(f"Failed to send to channel {channel_id}: {e}")
        
        # Increment user's post count for successful sends
        if sent_count > 0:
            await database.increment_user_post_count(user_id)
            
        await bot.send_message(user_id, get_text('broadcast_success', lang).format(count=sent_count))

    await state.clear()
