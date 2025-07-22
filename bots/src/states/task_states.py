from aiogram import F
from aiogram.fsm.state import StatesGroup, State


class CreateTaskStates(StatesGroup):
    waiting_title = State()
    waiting_description = State()
    waiting_deadline = State()
    waiting_tz = State()


class UpdateTaskStates(StatesGroup):
    waiting_title = State()
    waiting_description = State()
    waiting_deadline = State()

    @classmethod
    def resolve_state(cls, state: str):
        if state == 'title':
            return cls.waiting_title
        elif state == 'description':
            return cls.waiting_description
        else:
            return cls.waiting_deadline
