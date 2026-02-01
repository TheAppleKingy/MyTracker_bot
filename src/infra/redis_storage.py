
import json
from typing import Optional
from datetime import timezone, timedelta, datetime

from redis.asyncio import Redis

from src.application.interfaces import StorageInterface


def _to_json(reminders_tab: dict[str, datetime]):
    return json.dumps({k: v.isoformat() for k, v in reminders_tab.items()})


class RedisBotStorage(StorageInterface):
    def __init__(self, redis: Redis):
        self._redis = redis

    async def get_tz(self, tg_name: str) -> Optional[timezone]:
        offset = await self._redis.get(f"tz:{tg_name}")
        if not offset:
            return None
        return timezone(timedelta(minutes=(int(offset))))

    async def set_tz(self, tg_name: str, offset: int) -> None:
        await self._redis.set(f"tz:{tg_name}", offset)

    async def get_reminders_tab(self, tg_name: str) -> Optional[dict[str, datetime]]:
        tab = await self._redis.get(f"rms:{tg_name}")
        if not tab:
            return None
        decoded = json.loads(tab)
        return {k: datetime.fromisoformat(v).astimezone(timezone.utc) for k, v in decoded.items()}

    async def set_reminder(self, tg_name: str, eta: datetime, id_: str) -> None:
        tab = await self.get_reminders_tab(tg_name)
        if not tab:
            tab = {}
        tab[id_] = eta.astimezone(timezone.utc)
        await self._redis.set(f"rms:{tg_name}", _to_json(tab))

    async def get_reminder(self, tg_name: str, id_: str) -> Optional[datetime]:
        tab = await self.get_reminders_tab(tg_name)
        if not tab:
            return None
        return tab.get(id_)

    async def delete_reminder(self, tg_name: str, id_: str) -> None:
        tab = await self.get_reminders_tab(tg_name)
        if not tab:
            return None
        tab.pop(id_, None)
        await self._redis.set(f"rms:{tg_name}", _to_json(tab))
