from datetime import datetime, timedelta
from typing import Optional, Literal
from datetime import datetime, timezone

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram3_calendar import SimpleCalendar   # type: ignore


async def kalendar_kb(year: Optional[int] = None, month: Optional[int] = None):
    if not year:
        year = datetime.now().year
    if not month:
        month = datetime.now().month
    return await SimpleCalendar.start_calendar(year, month)


def time_kb(
    time_of: str,
    action: Literal['set', 'update'] = 'set',
    from_hour: int = 0,
    to_hour: int = 24
):
    builder = InlineKeyboardBuilder()
    buttons = [
        types.InlineKeyboardButton(
            text=f"0{i}h:00m" if i <= 9 else f"{i}h:00m",
            callback_data=f"{action}_{time_of}_hour_{i}"
        )
        for i in range(from_hour, to_hour)
    ]
    for i in range(0, len(buttons), 4):
        builder.row(*buttons[i:i+4])
    builder.row(types.InlineKeyboardButton(text="Enter manually", callback_data=f"{action}_{time_of}_hour_manually"))
    return builder.as_markup()


def deadline_time_kb(
        selected_date: datetime,
        for_update: bool = False,
):
    now_local = datetime.now(timezone.utc).astimezone(selected_date.tzinfo)
    action: Literal["set", "update"] = 'set'
    if for_update:
        action = 'update'
    if now_local.date() == selected_date.date():
        return time_kb('deadline', action, from_hour=now_local.hour + 1)
    if selected_date.date() > now_local.date():
        return time_kb('deadline', action)


def remind_time_kb(deadline_local: datetime, selected_date: datetime):
    user_tz = deadline_local.tzinfo
    now_local = datetime.now(timezone.utc).astimezone(user_tz)
    if deadline_local.date() == now_local.date():
        return time_kb('remind', from_hour=now_local.hour + 1, to_hour=deadline_local.hour)
    if deadline_local.date() > now_local.date():
        if now_local.date() == selected_date.date():
            return time_kb('remind', from_hour=now_local.hour + 1)
        if selected_date.date() == deadline_local.date():
            return time_kb('remind', to_hour=deadline_local.hour)
        return time_kb('remind')
