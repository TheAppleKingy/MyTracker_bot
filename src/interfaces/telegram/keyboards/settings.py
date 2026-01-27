from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def get_settings_kb():
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='/settings'))
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False
    )


def _next_tz_page_button(next_page: str):
    return types.InlineKeyboardButton(text='Next', callback_data=f'timezones_page_{next_page}')


def _prev_tz_page_button(prev_page: str):
    return types.InlineKeyboardButton(text='Prev', callback_data=f'timezones_page_{prev_page}')


def _set_timezone_button():
    return types.InlineKeyboardButton(text='Set timezone', callback_data='set_timezone')


def get_settings_list_kb():
    builder = InlineKeyboardBuilder()
    buttons = [_set_timezone_button()]
    builder.add(*buttons)
    builder.adjust(*[1]*len(buttons))
    return builder.as_markup()


def get_timezones_page_kb(page: int, step: int, timezones: list[str]):
    start_idx = page*step
    page_count = len(timezones) // step
    additional = [_prev_tz_page_button(page-1), _next_tz_page_button(page+1)]
    if page + 1 > page_count:
        additional = additional[:-1]
    elif page - 1 < 1:
        additional = additional[1:]
    if step > len(timezones):
        start_idx, step = 0, len(timezones)
        additional = []
    builder = InlineKeyboardBuilder()
    tz_buttons = [types.InlineKeyboardButton(
        text=tz, callback_data=f'tz={tz}') for tz in timezones[start_idx:start_idx+step]]
    builder.add(*tz_buttons)
    builder.adjust(*[1]*step)
    builder.row(*additional)
    return builder.as_markup()
