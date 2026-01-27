from aiogram.fsm.state import StatesGroup, State


class SetTZStates(StatesGroup):
    waiting_country = State()
    waiting_offset = State()
