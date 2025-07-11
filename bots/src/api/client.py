import httpx

import config

from redis.asyncio import from_url

from .response_handler import BackendResponse


class BackendClient:
    def __init__(self, for_tg_name: str = None):
        self.client = httpx.AsyncClient(base_url=config.BASE_API_URL)
        self.for_tg_name = for_tg_name
        self.redis = from_url(config.REDIS_URL, decode_responses=True)

    async def login(self, email: str, password: str):
        response = BackendResponse(await self.client.post(url='profile/login', json={'email': email, 'password': password}))
        token = self.client.cookies.get('token')
        await self.redis.set(f'token:{self.for_tg_name}', token)
        return response

    async def register(self, tg_name: str, email: str, first_name: str, last_name: str, password: str):
        data = {
            "tg_name": tg_name,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "password": password
        }
        return BackendResponse(await self.client.post(url='profile/request/registration', json=data))

    async def check_is_active(self):
        return BackendResponse(await self.client.post('bot/check_is_active', json={'tg_name': self.for_tg_name}))

    async def get_my_tasks(self):
        token = await self.redis.get(f'token:{self.for_tg_name}')
        return BackendResponse(await self.client.get('bot/my_tasks', cookies={'token': token}))

    async def get_my_task(self, task_id: int):
        token = await self.redis.get(f'token:{self.for_tg_name}')
        return BackendResponse(await self.client.get(f'bot/my_task/{task_id}', cookies={'token': token}))
