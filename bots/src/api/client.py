import httpx

from typing import Optional

import config

from .redis_client import set_user_token, get_token
from .response_handler import BackendResponse


class BackendClient:
    def __init__(self, for_tg_name: str = None):
        self.for_tg_name = for_tg_name

    async def _web_client(self, authed: bool = True):
        web = httpx.AsyncClient(base_url=config.BASE_API_URL)
        if authed:
            token = await get_token(self.for_tg_name)
            web.cookies.set('token', token)
        return web

    async def login(self, email: str, password: str):
        web = await self._web_client(authed=False)
        response = BackendResponse(await web.post(url='profile/login', json={'email': email, 'password': password}))
        token = web.cookies.get('token')
        await set_user_token(token, self.for_tg_name)
        return response

    async def register(self, tg_name: str, email: str, first_name: str, last_name: str, password: str):
        data = {
            "tg_name": tg_name,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "password": password
        }
        web = await self._web_client(authed=False)
        return BackendResponse(await web.post(url='profile/request/registration', json=data))

    async def check_is_active(self):
        web = await self._web_client(authed=False)
        return BackendResponse(await web.post('bot/check_is_active', json={'tg_name': self.for_tg_name}))

    async def get_my_tasks(self):
        web = await self._web_client()
        return BackendResponse(await web.get('bot/my_tasks'))

    async def get_my_task(self, task_id: int):
        web = await self._web_client()
        return BackendResponse(await web.get(f'bot/my_task/{task_id}'))

    async def create_task(self, title: str, description: str, creation_date: str, deadline: str, task_id: int = None):
        data = {
            'title': title,
            'description': description,
            'creation_date': creation_date,
            'deadline': deadline,
            'task_id': task_id,
        }
        web = await self._web_client()
        return BackendResponse(await web.post('bot/create_task', json=data))

    async def update_task(self, task_id: int, title: Optional[str] = None, description: Optional[str] = None, deadline: Optional[str] = None):
        data = {
            'title': title,
            'description': description,
            'deadline': deadline
        }
        web = await self._web_client()
        return BackendResponse(await web.patch(f"bot/update_task/{task_id}", json=data))

    async def finish_task(self, task_id: int):
        web = await self._web_client()
        return BackendResponse(await web.delete(f'bot/finish_task/{task_id}'))
