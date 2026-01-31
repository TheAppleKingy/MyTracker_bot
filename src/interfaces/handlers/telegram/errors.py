from typing import Optional

from aiogram.types import InlineKeyboardMarkup


class HandlerError(Exception):
    def __init__(
        self,
        *args,
        kb: Optional[InlineKeyboardMarkup] = None,
        clear_state: bool = True,
        add_last_message: bool = False,
    ):
        super().__init__(*args)
        self.kb = kb
        self.clear_state = clear_state
        self.add_last_message = add_last_message
