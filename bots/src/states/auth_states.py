from aiogram import F
from aiogram.fsm.state import StatesGroup, State


class LoginStates(StatesGroup):
    waiting_email = State()
    waiting_password = State()


class RegistrationStates(StatesGroup):
    waiting_email = State()
    waiting_first_name = State()
    waiting_last_name = State()
    waiting_password = State()
    waiting_tz = State()
