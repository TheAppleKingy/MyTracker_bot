import httpx

from typing import Union, Optional
from datetime import datetime

from application.interfaces.clients import BackendClientInterface
from src.application.interfaces.token_service import TokenServiceInterface
from src.domain.entities import Task


class URIs:
    _base = "/api/v1"

    @property
    def register(self):
        return self._base + "/auth/register"

    @property
    def check_registered(self):
        return self._base + "/auth/check"

    @property
    def create_task(self):
        return self._base + "/tasks"


class HttpBackendClient(BackendClientInterface):
    def __init__(
        self,
        base_url: str,
        token_service: TokenServiceInterface,
    ):
        self._base_url = base_url
        self._token_service = token_service
        self._uris = URIs()

    def _client(self):
        return httpx.AsyncClient(base_url=self._base_url)

    def _auth_client(self, tg_name: str):
        cl = self._client()
        cl.cookies.update({"token": self._token_service.generate_token(tg_name)})
        return cl

    def _handle_response(self, response: httpx.Response) -> Union[str, dict, bool, None]:
        if response.status_code == 401:
            return "Unable to recognize you. Try again or write to support"
        elif response.status_code == 403:
            return "You don't have permissions for this move"
        elif response.status_code == 400:
            return response.json().get("detail")
        elif response.status_code == 200:
            return response.json()
        else:
            return "Unexpected error. Try later or write to support"

    async def register(self, tg_name: str) -> None:
        resp = await self._client().post(self._uris.register, json={"tg_name": tg_name})
        return self._handle_response(resp)

    async def check_registered(self, tg_name: str) -> bool:
        resp = await self._client().get(self._uris.check_registered, params={"tg_name": tg_name})
        return self._handle_response(resp)

    async def create_task(
        self,
        tg_name: str,
        title: str,
        description: str,
        deadline: datetime,
        parent_id: Optional[int] = None
    ) -> Task:
        resp = await self._auth_client(tg_name).post(self._uris.create_task, json={
            "title": title,
            "description": description,
            "deadline": deadline.isoformat(),
            "parent_id": parent_id
        })
        data = self._handle_response(resp)
        return Task(**data)
