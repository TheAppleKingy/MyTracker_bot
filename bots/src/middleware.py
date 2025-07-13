from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from api.exc import BackendError, NotAuthenticatedError
from keyboards.auth import login_kb


class BackendResponseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except NotAuthenticatedError as e:
            if isinstance(event, CallbackQuery):
                await event.message.answer('You have to login', reply_markup=login_kb())
            elif isinstance(event, Message):
                await event.answer('You have to login', reply_markup=login_kb())
            return
        except BackendError as e:
            if isinstance(event, CallbackQuery):
                await event.message.answer(str(e))
            elif isinstance(event, Message):
                await event.answer(str(e))
            return
