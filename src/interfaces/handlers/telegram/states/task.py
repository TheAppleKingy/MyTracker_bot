from aiogram.fsm.state import StatesGroup, State


class CreateTaskStates(StatesGroup):
    waiting_title = State()
    waiting_description = State()
    waiting_deadline_date = State()
    waiting_deadline_time = State()


class UpdateTaskStates(StatesGroup):
    waiting_text_data = State()
    waiting_deadline_date = State()
    waiting_deadline_time = State()


class RemindState(StatesGroup):
    waiting_remind_date = State()
    waiting_remind_time = State()
