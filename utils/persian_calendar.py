import jdatetime
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- Constants for Calendar ---
MONTHS = [
    "فروردین", "اردیبهشت", "خرداد",
    "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر",
    "دی", "بهمن", "اسفند"
]
DAYS_OF_WEEK = ["ش", "ی", "د", "س", "چ", "پ", "ج"]

# --- Callback Data Prefixes ---
CALENDAR_CALLBACK_PREFIX = "pcal"
IGNORE_CALLBACK = f"{CALENDAR_CALLBACK_PREFIX}_ignore"
PREV_MONTH_CALLBACK = f"{CALENDAR_CALLBACK_PREFIX}_prev"
NEXT_MONTH_CALLBACK = f"{CALENDAR_CALLBACK_PREFIX}_next"
DAY_CALLBACK = f"{CALENDAR_CALLBACK_PREFIX}_day"


async def create_persian_calendar(year: int = None, month: int = None) -> InlineKeyboardMarkup:
    """
    Creates an inline keyboard with a Persian (Jalali) calendar for the given month and year.
    If year and month are not provided, it will use the current month.
    """
    if year is None or month is None:
        today = jdatetime.date.today()
        year, month = today.year, today.month

    builder = InlineKeyboardBuilder()

    # Month and Year header
    builder.row(
        builder.button(text=f"{MONTHS[month-1]} {year}", callback_data=IGNORE_CALLBACK)
    )

    # Days of the week header
    row = [builder.button(text=day, callback_data=IGNORE_CALLBACK) for day in DAYS_OF_WEEK]
    builder.row(*row)

    # Calendar days
    month_start_day = jdatetime.date(year, month, 1).weekday()
    days_in_month = jdatetime.date(year, month, 1).daysinmonth

    # Add empty buttons for the first week's offset
    calendar_days = [builder.button(text=" ", callback_data=IGNORE_CALLBACK)] * month_start_day

    # Add day buttons
    for day in range(1, days_in_month + 1):
        calendar_days.append(
            builder.button(text=str(day), callback_data=f"{DAY_CALLBACK}_{year}_{month}_{day}")
        )

    # Reshape the list of buttons into a 7-column grid
    for i in range(0, len(calendar_days), 7):
        builder.row(*calendar_days[i:i+7])

    # Navigation buttons
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    builder.row(
        builder.button(text="<", callback_data=f"{PREV_MONTH_CALLBACK}_{prev_year}_{prev_month}"),
        builder.button(text=">", callback_data=f"{NEXT_MONTH_CALLBACK}_{next_year}_{next_month}")
    )

    return builder.as_markup()
