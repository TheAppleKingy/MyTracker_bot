from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


def _registration_button():
    return types.InlineKeyboardButton(text="Register", callback_data="register")


def get_start_kb():
    builder = InlineKeyboardBuilder()
    builder.add(
        _registration_button()
    )
    return builder.as_markup()
