from datetime import timezone, timedelta

from config import redis
from .exc import NotAuthenticatedError, NoTimezoneError


async def get_user_tz(for_user: str):
    tz_val = await redis.get(f'tz:{for_user}')
    if not tz_val:
        raise NoTimezoneError('No timezone info about user')
    return timezone(timedelta(hours=int(tz_val)))


async def get_token(for_user: str) -> str:
    token = await redis.get(f'token:{for_user}')
    if not token:
        raise NotAuthenticatedError('No token in memory storage')
    return token


async def set_user_tz_val(tz_val: str | int, for_user: str):
    await redis.set(f'tz:{for_user}', str(tz_val))


async def set_user_token(token: str, for_user: str):
    await redis.set(f'token:{for_user}', token)
