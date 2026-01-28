from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


def _active_tasks_button():
    return types.InlineKeyboardButton(text="Active tasks", callback_data="get_active_tasks")


def _finished_tasks_button():
    return types.InlineKeyboardButton(text="Finished tasks", callback_data="get_finished_tasks")


def _back_button(callback_data: str):
    return types.InlineKeyboardButton(text="Back", callback_data=callback_data)


def _settings_button():
    return types.InlineKeyboardButton(text="Settings", callback_data="settings")


def _main_button():
    return types.InlineKeyboardButton(text="Main page", callback_data='main_page')


def back_kb(callback_data: str):
    builder = InlineKeyboardBuilder()
    builder.add(_back_button(callback_data))
    return builder.as_markup()


def main_kb():
    builder = InlineKeyboardBuilder()
    builder.add(_active_tasks_button(), _finished_tasks_button(), _settings_button())
    builder.adjust(*[1]*3)
    return builder.as_markup()


def main_page_kb():
    builder = InlineKeyboardBuilder()
    builder.add(_main_button())
    return builder.as_markup()
