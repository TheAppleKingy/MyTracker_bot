from datetime import timezone

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


from .shared import _back_button


def get_timezone_view(offset_min: int) -> str:
    sign = "-" if offset_min < 0 else "+"
    hours = abs(offset_min) // 60
    mins = abs(offset_min) - 60 * hours
    return f"UTC{sign}{hours}:{0 if mins < 10 else ""}{mins}"


def _next_tz_page_button(next_page: str):
    return types.InlineKeyboardButton(text='Next', callback_data=f'timezones_page_{next_page}')


def _prev_tz_page_button(prev_page: str):
    return types.InlineKeyboardButton(text='Prev', callback_data=f'timezones_page_{prev_page}')


def _set_timezone_button():
    return types.InlineKeyboardButton(text='Set timezone', callback_data='set_timezone')


def _tz_button(offset_min: int):
    return types.InlineKeyboardButton(
        text=get_timezone_view(offset_min),
        callback_data=f"set_tz_offset_{offset_min}"
    )


def settings_list_kb():
    builder = InlineKeyboardBuilder()
    buttons = [_set_timezone_button(), _back_button("main_page")]
    builder.add(*buttons)
    builder.adjust(*[1]*len(buttons))
    return builder.as_markup()


def timezones_page_kb(page: int, step: int, offsets: list[int]):
    start_idx = (page - 1) * step
    page_count = len(offsets) // step + 1
    additional = [_prev_tz_page_button(page-1), _next_tz_page_button(page+1)]
    if page >= page_count:
        additional = additional[:-1]
    elif page <= 1:
        additional = additional[1:]
    if step > len(offsets):
        start_idx, step = 0, len(offsets)
        additional = []
    builder = InlineKeyboardBuilder()
    tz_buttons = [_tz_button(tz) for tz in offsets[start_idx:start_idx+step]]
    builder.add(*tz_buttons)
    builder.adjust(*[1]*step)
    builder.row(*additional)
    return builder.as_markup()
