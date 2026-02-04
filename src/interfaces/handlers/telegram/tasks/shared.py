from datetime import datetime, timezone, timedelta

from src.application.interfaces import AsyncStorageInterface
from src.application.interfaces.services import NotifyServiceInterface
from src.application.interfaces.clients import BackendClientInterface
from src.domain.entities import Task
from src.interfaces.handlers.telegram.errors import HandlerError
from src.interfaces.presentators.telegram.keyboards.shared import back_kb
from src.interfaces.presentators.time import show_timedelta_verbose

__all__ = [
    "ChangeDeadline",
    "SetReminder",
    "ForceFinishTask",
    "FinishTask"
]


class BaseUseCase:
    def __init__(
        self,
        backend: BackendClientInterface,
        notify_service: NotifyServiceInterface,
        storage: AsyncStorageInterface
    ):
        self._backend = backend
        self._storage = storage
        self._notify_service = notify_service


class ChangeDeadline(BaseUseCase):
    async def execute(self, username: str, new_deadline: datetime, updating_task_id: int) -> Task:
        ok, res = await self._backend.update_task(username, updating_task_id, deadline=new_deadline)
        if not ok:
            raise HandlerError(res, kb=back_kb(f"get_task_{updating_task_id}"))
        reminders_map = await self._storage.get_reminders_tab(username, updating_task_id)
        if reminders_map:
            to_revoke = []
            for reminder_id, eta in reminders_map.items():
                if eta > new_deadline.astimezone(timezone.utc):
                    to_revoke.append(reminder_id)
                    self._notify_service.revoke_reminder(reminder_id)
            await self._storage.delete_reminders(username, to_revoke, updating_task_id)
        return res


class SetReminder:
    def __init__(
        self,
        notify_service: NotifyServiceInterface,
        storage: AsyncStorageInterface
    ):
        self._notify_service = notify_service
        self._storage = storage

    async def exeute(
        self,
        chat_id: int,
        remining_time: timedelta,
        eta: datetime,
        username: str,
        task_id: int,
        task_title: str
    ):
        delta_str = show_timedelta_verbose(remining_time)
        msg = f'<b>Task "{task_title}" is waiting! Deadline over ' + delta_str + "</b>"
        id_ = self._notify_service.send_notify(username, task_id, msg, chat_id, eta)
        await self._storage.set_reminder(username, eta, id_, task_id)


class ForceFinishTask(BaseUseCase):
    async def execute(self, username: str, task_id: int):
        ok, res = await self._backend.force_finish_task(username, task_id)
        if not ok:
            raise HandlerError(res, kb=back_kb(f"get_task_{task_id}"))
        to_revoke = await self._storage.delete_all_reminders(username, task_id)
        for sub_id in res:
            to_revoke.extend(await self._storage.delete_all_reminders(username, sub_id))
        for reminder_id in to_revoke:
            self._notify_service.revoke_reminder(reminder_id)


class FinishTask(BaseUseCase):
    async def execute(self, username: str, task_id: int):
        ok, res = await self._backend.finish_task(username, task_id)
        if not ok:
            raise HandlerError(res, kb=back_kb(f"get_task_{task_id}"))
        to_revoke = await self._storage.delete_all_reminders(username, task_id)
        for reminder_id in to_revoke:
            self._notify_service.revoke_reminder(reminder_id)
