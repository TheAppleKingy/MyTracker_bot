from typing import Protocol, Optional
from datetime import timezone


class TimezoneClientInterface(Protocol):
    async def get_tz(self, tg_name: str) -> Optional[timezone]: ...
    async def set_tz(self, tg_name: str) -> None: ...
