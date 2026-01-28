from typing import Optional
from datetime import timezone, timedelta

from redis.asyncio import Redis

from src.application.interfaces import StorageInterface


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
