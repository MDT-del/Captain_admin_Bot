import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.exceptions import TelegramBadRequest

from config import BOT_TOKEN
from texts import get_text
import database
from states import Form

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=storage)


# --- Keyboards ---
def get_language_keyboard() -> InlineKeyboardMarkup:
    buttons = [[
        InlineKeyboardButton(text=get_text('choose_language_button', 'fa'), callback_data="lang_fa"),
        InlineKeyboardButton(text=get_text('choose_language_button', 'en'), callback_data="lang_en")
    ]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_main_menu_keyboard(lang: str) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text=get_text('set_footer_button', lang))],
        [KeyboardButton(text=get_text('manage_channels_button', lang))]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_channels_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=get_text('add_channel_button', lang), callback_data="add_channel")],
        [InlineKeyboardButton(text=get_text('my_channels_button', lang), callback_data="my_channels")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# --- Command Handlers ---
@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.answer(f"{get_text('welcome', 'fa')}\n{get_text('welcome', 'en')}", reply_markup=get_language_keyboard())

@dp.message(Command("menu"))
async def show_menu(message: types.Message):
    lang = await database.get_user_language(message.from_user.id) or 'en'
    await message.answer(get_text('main_menu', lang), reply_markup=get_main_menu_keyboard(lang))


# --- Language and Menu Handlers ---
@dp.callback_query(F.data.startswith("lang_"))
async def process_language_selection(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]
    await database.add_or_update_user(callback.from_user.id, lang)
    await callback.answer()
    await callback.message.edit_text(get_text('lang_selected', lang))
    await callback.message.answer(get_text('main_menu', lang), reply_markup=get_main_menu_keyboard(lang))

@dp.message(F.text.in_([get_text('manage_channels_button', 'fa'), get_text('manage_channels_button', 'en')]))
async def show_channels_menu(message: types.Message):
    lang = await database.get_user_language(message.from_user.id) or 'en'
    await message.answer(get_text('channels_menu_title', lang), reply_markup=get_channels_menu_keyboard(lang))


# --- Footer Setting Handlers ---
@dp.message(F.text.in_([get_text('set_footer_button', 'fa'), get_text('set_footer_button', 'en')]))
async def prompt_for_footer(message: types.Message, state: FSMContext):
    lang = await database.get_user_language(message.from_user.id) or 'en'
    await state.set_state(Form.waiting_for_footer)
    await message.answer(get_text('prompt_for_footer', lang))

@dp.message(Form.waiting_for_footer, F.text)
async def process_footer_text(message: types.Message, state: FSMContext):
    lang = await database.get_user_language(message.from_user.id) or 'en'
    await database.set_footer_text(message.from_user.id, message.text)
    await state.clear()
    await message.answer(get_text('footer_set_success', lang), reply_markup=get_main_menu_keyboard(lang))


# --- Channel Management Handlers ---
@dp.callback_query(F.data == "add_channel")
async def prompt_for_channel_forward(callback: types.CallbackQuery, state: FSMContext):
    lang = await database.get_user_language(callback.from_user.id) or 'en'
    await state.set_state(Form.waiting_for_channel_forward)
    await callback.message.edit_text(get_text('prompt_forward_message', lang))
    await callback.answer()

@dp.message(Form.waiting_for_channel_forward, F.forward_from_chat)
async def process_channel_forward(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await database.get_user_language(user_id) or 'en'
    channel_id = message.forward_from_chat.id

    # Check if channel is already registered by this user
    if await database.is_channel_registered(channel_id, user_id):
        await message.answer(get_text('channel_already_registered', lang))
        await state.clear()
        return

    try:
        # Check if the bot is an admin
        bot_member = await bot.get_chat_member(chat_id=channel_id, user_id=bot.id)
        if bot_member.status not in ['administrator', 'creator']:
            await message.answer(get_text('error_bot_not_admin', lang))
            await state.clear()
            return

        # Check if the user is an admin
        user_member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        if user_member.status not in ['administrator', 'creator']:
            await message.answer(get_text('error_not_admin_in_channel', lang))
            await state.clear()
            return

        # If all checks pass, add the channel
        await database.add_channel(channel_id, user_id)
        await message.answer(get_text('channel_add_success', lang))

    except TelegramBadRequest as e:
        logging.error(f"Error checking admin status for channel {channel_id}: {e}")
        await message.answer(get_text('error_generic', lang))
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        await message.answer(get_text('error_generic', lang))
    finally:
        await state.clear()

@dp.callback_query(F.data == "my_channels")
async def list_my_channels(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = await database.get_user_language(user_id) or 'en'
    channels = await database.get_user_channels(user_id)

    if not channels:
        await callback.message.edit_text(get_text('no_channels_found', lang))
    else:
        response_text = f"<b>{get_text('your_channels_list', lang)}</b>\n\n"
        for channel in channels:
            try:
                chat = await bot.get_chat(channel[0])
                response_text += f"- {chat.title} (<code>{chat.id}</code>)\n"
            except Exception:
                response_text += f"- Unknown Channel (<code>{channel[0]}</code>)\n"
        await callback.message.edit_text(response_text)

    await callback.answer()


# --- Main Execution ---
async def main():
    await database.init_db()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
