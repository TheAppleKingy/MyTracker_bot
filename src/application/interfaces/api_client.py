from typing import Protocol


class BackendClientInterface(Protocol):
    async def register(self, tg_name: str) -> None: ...
