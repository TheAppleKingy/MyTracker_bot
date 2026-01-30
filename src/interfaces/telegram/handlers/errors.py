from typing import Optional

from aiogram.types import InlineKeyboardMarkup


class HandlerError(Exception):
    def __init__(self, *args, kb: Optional[InlineKeyboardMarkup] = None, clear_state: bool = True):
        super().__init__(*args)
        self.kb = kb
        self.clear_state = clear_state
