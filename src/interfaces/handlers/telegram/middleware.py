from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, TelegramObject
from aiogram.fsm.context import FSMContext

from src.interfaces.handlers.telegram.errors import HandlerError
from src.logger import logger


async def _clear_state(data: dict[str, Any]):
    context: FSMContext = data.get('context')  # type: ignore
    if context:
        await context.clear()


class HandleErrorMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        answer = event.message.answer if isinstance(event, CallbackQuery) else event.answer  # type: ignore
        try:
            data["context"] = data.pop("state")
            return await handler(event, data)
        except HandlerError as e:
            if e.clear_state:
                await _clear_state(data)
            res = await answer(text=f"<b>{str(e)}</b>", reply_markup=e.kb, parse_mode="HTML")
            if e.add_last_message:
                await data["context"].update_data(last_message=res.message_id)
            return
        except Exception as e:
            await _clear_state(data)
            logger.exception(f"{e}")
            return await answer(
                text="<b>Service unaccessible. Try later or write to support</b>",
                reply_markup=None,
                parse_mode="HTML"
            )


# class RollbackDetectorMiddleware(BaseMiddleware):
#     """this middleware detected messages that bot sending what could be rollback"""

#     async def __call__(
#         self,
#         handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
#         event: TelegramObject,
#         data: Dict[str, Any]
#     ) -> Any:
#         message = await handler(event, data)
#         if message:
#             if isinstance(message, Message):
#                 state: FSMContext = data.get('state')
#                 if state:
#                     await state.update_data(rollback_msg=message.message_id)
#         return message
