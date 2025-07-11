from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.command import Command


def check_active_kb():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="I confirmed registration", callback_data='reg_confirmed'))
    return builder.as_markup()


def login_kb():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Login", callback_data='login_start'))
    return builder.as_markup()
