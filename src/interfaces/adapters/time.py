from datetime import datetime

from src.interfaces.handlers.telegram.errors import HandlerError


def validate_time(time_str: str):
    try:
        return datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        raise HandlerError("Invalid time format. Try again", clear_state=False)
