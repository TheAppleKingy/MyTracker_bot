from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from src.interfaces.telegram.keyboards.tasks import get_my_tasks_kb


class HandledError(Exception):
    def __init__(self, *args, kb: InlineKeyboardMarkup | ReplyKeyboardMarkup | None = get_my_tasks_kb()):
        super().__init__(*args)
        self.kb = kb
