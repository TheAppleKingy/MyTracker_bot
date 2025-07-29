from aiogram.fsm.state import StatesGroup, State


class CreateTaskStates(StatesGroup):
    waiting_title = State()
    waiting_description = State()
    waiting_deadline = State()
    waiting_notify_time = State()


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


class RemindTimeCountState(StatesGroup):
    waiting_remind_time_info = State()
    waiting_weeks_count = State()
    waiting_days_count = State()
    waiting_hours_count = State()
    waiting_one_more_reminder = State()

    @classmethod
    def resolve_state(cls, state: str):
        if state == 'weeks':
            return cls.waiting_weeks_count
        elif state == 'days':
            return cls.waiting_days_count
        else:
            return cls.waiting_hours_count
