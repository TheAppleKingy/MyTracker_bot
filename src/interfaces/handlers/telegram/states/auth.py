from aiogram.fsm.state import StatesGroup, State


class RegistrationStates(StatesGroup):
    waiting_email = State()
