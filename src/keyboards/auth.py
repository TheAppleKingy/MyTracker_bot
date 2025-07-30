from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


def login_button():
    return types.InlineKeyboardButton(
        text="Login", callback_data='login_start')


def registration_button():
    return types.InlineKeyboardButton(text="Register", callback_data="reg_start")


def get_start_kb():
    builder = InlineKeyboardBuilder()
    builder.add(
        login_button(),
        registration_button()
    )
    builder.adjust(2)
    return builder.as_markup()


def check_active_kb():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="I confirmed registration", callback_data='reg_confirmed'))
    return builder.as_markup()


def login_kb():
    builder = InlineKeyboardBuilder()
    builder.add(login_button())
    return builder.as_markup()
