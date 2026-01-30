from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from src.interfaces.telegram.handlers.errors import HandlerError
from src.logger import logger


async def _clear_state(data: dict[str]):
    state: FSMContext = data.get('state')
    if state:
        await state.clear()


class HandleErrorMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        answer = event.message.answer if isinstance(event, CallbackQuery) else event.answer
        try:
            return await handler(event, data)
        except HandlerError as e:
            if e.clear_state:
                await _clear_state(data)
            return await answer(text=f"<b>{str(e)}</b>", reply_markup=e.kb, parse_mode="HTML")
        except Exception:
            await _clear_state(data)
            return await answer(text="Service unaccessible. Try later or write to support", reply_markup=None)


class RollbackDetectorMiddleware(BaseMiddleware):
    """this middleware detected messages that bot sending what could be rollback"""

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        message = await handler(event, data)
        if message:
            if isinstance(message, Message):
                state: FSMContext = data.get('state')
                if state:
                    await state.update_data(rollback_msg=message.message_id)
        return message
