from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


def build_inline_keyboard(*button_data: dict[str, str], adjust: int):
    builder = InlineKeyboardBuilder()
    builder.add(**(types.InlineKeyboardButton(**button)
                for button in button_data))
    builder.adjust(adjust)
    return builder.as_markup()
