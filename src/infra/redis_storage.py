import json
from typing import Optional
from datetime import timezone, timedelta, datetime

from redis.asyncio import Redis
from redis import Redis as SyncRedis


from src.logger import logger
from src.application.interfaces import AsyncStorageInterface, SyncStorageInterface


def _to_json(reminders_tab: dict[str, datetime]):
    return json.dumps({k: v.isoformat() for k, v in reminders_tab.items()})


class AsyncRedisBotStorage(AsyncStorageInterface):
    def __init__(self, redis: Redis):
        self._redis = redis

    async def get_tz(self, tg_name: str) -> Optional[timezone]:
        offset = await self._redis.get(f"tz:{tg_name}")
        if not offset:
            return None
        return timezone(timedelta(minutes=(int(offset))))

    async def set_tz(self, tg_name: str, offset: int) -> None:
        await self._redis.set(f"tz:{tg_name}", offset)

    async def get_reminders_tab(self, tg_name: str, task_id: int) -> Optional[dict[str, datetime]]:
        tab = await self._redis.get(f"rms:{tg_name}:{task_id}")
        if not tab:
            return None
        decoded = json.loads(tab)
        return {k: datetime.fromisoformat(v).astimezone(timezone.utc) for k, v in decoded.items()}

    async def set_reminder(self, tg_name: str, eta: datetime, id_: str, task_id: int) -> None:
        tab = await self.get_reminders_tab(tg_name, task_id)
        if not tab:
            tab = {}
        tab[id_] = eta.astimezone(timezone.utc)
        await self._redis.set(f"rms:{tg_name}:{task_id}", _to_json(tab))

    async def get_reminder(self, tg_name: str, id_: str, task_id: int) -> Optional[datetime]:
        tab = await self.get_reminders_tab(tg_name, task_id)
        if not tab:
            return None
        return tab.get(id_)

    async def delete_reminders(self, tg_name: str, reminders_ids: list[str], task_id: int) -> None:
        tab = await self.get_reminders_tab(tg_name, task_id)
        if not tab:
            return None
        for id_ in reminders_ids:
            tab.pop(id_, None)
        if not tab:
            await self._redis.delete(f"rms:{tg_name}:{task_id}")
        else:
            await self._redis.set(f"rms:{tg_name}:{task_id}", _to_json(tab))

    async def delete_all_reminders(self, tg_name: str, task_id: int) -> list[str]:
        tab = await self.get_reminders_tab(tg_name, task_id)
        if not tab:
            return []
        await self._redis.delete(f"rms:{tg_name}:{task_id}")
        return list(tab.keys())


class SyncRedisBotStorage(SyncStorageInterface):
    def __init__(self, redis: SyncRedis):
        self._redis = redis

    def get_reminders_tab(self, tg_name: str, task_id: int) -> Optional[dict[str, datetime]]:
        tab = self._redis.get(f"rms:{tg_name}:{task_id}")
        if not tab:
            return None
        decoded = json.loads(tab)
        return {k: datetime.fromisoformat(v).astimezone(timezone.utc) for k, v in decoded.items()}

    def delete_reminders(self, tg_name: str, reminders_ids: list[str], task_id: int) -> None:
        tab = self.get_reminders_tab(tg_name, task_id)
        if not tab:
            return None
        for id_ in reminders_ids:
            tab.pop(id_, None)
        if not tab:
            self._redis.delete(f"rms:{tg_name}:{task_id}")
        else:
            self._redis.set(f"rms:{tg_name}:{task_id}", _to_json(tab))
