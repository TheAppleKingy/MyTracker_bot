from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from api.exc import BackendError, NotAuthenticatedError, NoTimezoneError
from keyboards.auth import login_kb
from keyboards.tasks import back_kb


class BackendResponseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            answer = event.message.answer if isinstance(
                event, CallbackQuery) else event.answer
            if isinstance(e, BackendError):
                if 'Unable to find user with email' in str(e):
                    await answer(
                        f"No user with email {str(e).split()[-1]}. Try again", reply_markup=login_kb())
                elif 'Cannot finish task' in str(e):
                    task_id = int(str(e).split()[3])
                    await answer('Cannot finish task while subtasks was not finished', reply_markup=back_kb(task_id))
                elif 'User not active' in str(e):
                    await answer("You did not follow the link. Confirm registration by following the link in mail and try again")
                if isinstance(e, NotAuthenticatedError):
                    await answer('You have to login', reply_markup=login_kb())
            if isinstance(e, NoTimezoneError):
                await answer("You have to go to settings and define your timezone")
            state: FSMContext = data.get('state')
            if state:
                await state.clear()
            return


class RollbackDetectorMiddleware(BaseMiddleware):
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
