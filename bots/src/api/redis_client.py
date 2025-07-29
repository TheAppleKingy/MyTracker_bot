from zoneinfo import ZoneInfo
from datetime import timezone, timedelta

from redis.asyncio import from_url

from config import REDIS_URL
from .exc import NotAuthenticatedError, NoTimezoneError


redis = from_url(REDIS_URL, decode_responses=True)


async def get_user_tz(for_user: str):
    """If tzinfo looks like 'Europe/CityName' then use ZoneInfo obj, else storage should store tzinfo as signed int representing offset"""
    tz_info = await redis.get(f'tz:{for_user}')
    if not tz_info:
        raise NoTimezoneError('No timezone info about user')
    if '/' in tz_info:
        return ZoneInfo(tz_info)
    return timezone(timedelta(hours=int(tz_info)))


async def get_token(for_user: str) -> str:
    token = await redis.get(f'token:{for_user}')
    if not token:
        raise NotAuthenticatedError('No token in memory storage')
    return token


async def set_user_tz(tz: str, for_user: str):
    await redis.set(f'tz:{for_user}', tz)


async def set_user_token(token: str, for_user: str):
    await redis.set(f'token:{for_user}', token)
