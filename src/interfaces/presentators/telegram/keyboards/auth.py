from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


def _registration_button():
    return types.InlineKeyboardButton(text="Register", callback_data="register")


def register_kb():
    builder = InlineKeyboardBuilder()
    builder.add(
        _registration_button()
    )
    return builder.as_markup()
