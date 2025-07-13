from aiogram import F
from aiogram.fsm.state import StatesGroup, State


class CreateTaskStates(StatesGroup):
    waiting_title = State()
    waiting_description = State()
    waiting_deadline = State()
    waiting_tz = State()
