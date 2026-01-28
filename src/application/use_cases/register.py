from src.application.interfaces.clients import BackendClientInterface


class RegisterUseCase:
    def __init__(
        self,
        backend: BackendClientInterface
    ):
        self._backend = backend

    async def execute(self, tg_name: str):
        return await self._backend.register(tg_name)
