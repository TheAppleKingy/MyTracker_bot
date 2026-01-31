# mypy: disable-error-code=return-value
import httpx
from typing import Union, Optional, Literal, TypeVar
from datetime import datetime

from src.application.interfaces.clients import BackendClientInterface, BackendResponse
from src.application.interfaces.services import TokenServiceInterface
from src.application.dto.task import TaskViewSchema
from src.domain.entities import Task, TaskPreview
from src.logger import logger


class URIs:
    _base = "/api/v1"

    @property
    def register(self):
        return self._base + "/auth/register"

    @property
    def check_registered(self):
        return self._base + "/auth/check"

    @property
    def tasks(self):
        return self._base + "/tasks"

    def task_info(self, task_id: int):
        return self.tasks + f"/{task_id}"

    def subtasks(self, parent_id: int):
        return self.task_info(parent_id) + "/subtasks"

    def check_task_active(self, task_id: int):
        return self.task_info(task_id) + "/is_active"

    def finish_task(self, task_id: int):
        return self.task_info(task_id) + "/finish"

    def force_finish_task(self, task_id: int):
        return self.finish_task(task_id) + "/force"

    def get_parent_id(self, task_id: int):
        return self.task_info(task_id) + "/parent"


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

    def _handle_response(self, response: httpx.Response) -> BackendResponse[Union[str, dict, list, bool, None]]:
        if response.status_code == 401:
            return False, "Unable to recognize you. Try again or write to support"
        elif response.status_code == 403:
            return False, "You don't have permissions for this move. Try again or write to support"
        elif response.status_code == 404:
            return False, "Resource does not exists"
        elif response.status_code == 400:
            return False, response.json().get("detail")
        elif response.status_code == 200:
            return True, response.json()
        else:
            return False, "Unexpected error. Try later or write to support"

    async def register(self, tg_name: str) -> BackendResponse[Optional[str]]:
        resp = await self._client().post(self._uris.register, json={"tg_name": tg_name})
        return self._handle_response(resp)

    async def check_registered(self, tg_name: str) -> BackendResponse[bool]:
        resp = await self._client().get(self._uris.check_registered, params={"tg_name": tg_name})
        return self._handle_response(resp)

    async def create_task(
        self,
        tg_name: str,
        title: str,
        description: str,
        deadline: datetime,
        parent_id: Optional[int] = None
    ) -> BackendResponse[Task]:
        resp = await self._auth_client(tg_name).post(self._uris.tasks, json={
            "title": title,
            "description": description,
            "deadline": deadline.isoformat(),
            "parent_id": parent_id
        })
        ok, data = self._handle_response(resp)
        return ok, Task(**TaskViewSchema.model_validate(data).model_dump()) if ok else data

    async def _get_paginated_tasks(
        self,
        url: str,
        tg_name: str,
        page: int,
        size: int,
        params: dict = {},
    ) -> BackendResponse[tuple[int, int, list[TaskPreview]]]:
        resp = await self._auth_client(tg_name).get(
            url,
            params={"page": page, "size": size, **params}
        )
        ok, data = self._handle_response(resp)
        if not ok:
            return False, data
        return True, (
            data["prev_page"],  # type: ignore
            data["next_page"],  # type: ignore
            [TaskPreview(**task_data) for task_data in data["tasks"]],  # type: ignore
        )

    async def get_tasks(
        self,
        tg_name: str,
        status: Literal["active", "finished"],
        page: int = 1,
        size: int = 5
    ) -> BackendResponse[tuple[int, int, list[TaskPreview]]]:
        return await self._get_paginated_tasks(self._uris.tasks, tg_name, page, size, {"status": status})

    async def get_task(self, tg_name: str, task_id: int) -> BackendResponse[Task]:
        resp = await self._auth_client(tg_name).get(self._uris.task_info(task_id))
        ok, data = self._handle_response(resp)
        if not ok:
            return False, data
        model = TaskViewSchema.model_validate(data)
        return True, Task(**model.model_dump())

    async def get_subtasks(
        self,
        tg_name: str,
        status: Literal["active", "finished"],
        parent_id: int,
        page: int = 1,
        size: int = 5
    ) -> BackendResponse[tuple[int, int, list[TaskPreview]]]:
        return await self._get_paginated_tasks(self._uris.subtasks(parent_id), tg_name, page, size, params={"status": status})

    async def delete_task(self, tg_name: str, task_id: int) -> BackendResponse[None]:
        resp = await self._auth_client(tg_name).delete(self._uris.task_info(task_id))
        return self._handle_response(resp)

    async def update_task(
        self,
        tg_name: str,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        deadline: Optional[datetime] = None
    ) -> BackendResponse[TaskPreview]:
        data = {}
        if title:
            data["title"] = title
        if description:
            data["description"] = description
        if deadline:
            data["deadline"] = deadline.isoformat()
        resp = await self._auth_client(tg_name).patch(self._uris.task_info(task_id), json=data)
        ok, data = self._handle_response(resp)
        return ok, Task(**TaskViewSchema.model_validate(data).model_dump()) if ok else data

    async def finish_task(self, tg_name: int, task_id: int) -> BackendResponse[None]:
        resp = await self._auth_client(tg_name).patch(self._uris.finish_task(task_id))
        return self._handle_response(resp)

    async def force_finish_task(self, tg_name: int, task_id: int) -> BackendResponse[None]:
        resp = await self._auth_client(tg_name).patch(self._uris.force_finish_task(task_id))
        return self._handle_response(resp)

    async def check_task_active(self, tg_name: str, task_id: int) -> BackendResponse[bool]:
        resp = await self._auth_client(tg_name).get(self._uris.check_task_active(task_id))
        return self._handle_response(resp)
