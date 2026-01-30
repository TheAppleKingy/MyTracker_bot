from typing import Literal

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


def _back_button(callback_data: str):
    return types.InlineKeyboardButton(text="Back", callback_data=callback_data)


def _settings_button():
    return types.InlineKeyboardButton(text="Settings", callback_data="settings")


def _main_button():
    return types.InlineKeyboardButton(text="Main page", callback_data='main_page')


def _tasks_button(status: Literal["active", "finished"], page: int):
    return types.InlineKeyboardButton(text=f"{status.capitalize()} tasks", callback_data=f"get_tasks_{status}_{page}")


def _next_button(callback_data: str):
    return types.InlineKeyboardButton(text=">", callback_data=callback_data)


def _prev_button(callback_data: str):
    return types.InlineKeyboardButton(text="<", callback_data=callback_data)


def back_kb(callback_data: str):
    builder = InlineKeyboardBuilder()
    builder.add(_back_button(callback_data))
    return builder.as_markup()


def main_kb():
    builder = InlineKeyboardBuilder()
    builder.add(_tasks_button("active", 1), _tasks_button("finished", 1), _settings_button())
    builder.adjust(*[1]*3)
    return builder.as_markup()


def main_page_kb():
    builder = InlineKeyboardBuilder()
    builder.add(_main_button())
    return builder.as_markup()
