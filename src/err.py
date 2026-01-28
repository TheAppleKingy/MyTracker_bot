from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from src.interfaces.telegram.keyboards.shared import main_page_kb


class HandledError(Exception):
    def __init__(self, *args, kb: InlineKeyboardMarkup | ReplyKeyboardMarkup | None = main_page_kb()):
        super().__init__(*args)
        self.kb = kb
