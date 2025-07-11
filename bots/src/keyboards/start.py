from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_start_kb():
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(text="Login", callback_data="login_start"),
        types.InlineKeyboardButton(text="Register", callback_data="reg_start")
    )
    builder.adjust(2)
    return builder.as_markup()
