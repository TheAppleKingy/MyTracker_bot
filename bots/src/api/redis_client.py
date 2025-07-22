from datetime import timezone, timedelta

from config import redis


async def get_user_tz(for_user: str):
    tz_val = await redis.get(f'tz:{for_user}')
    if not tz_val:
        return None
    return timezone(timedelta(hours=int(tz_val)))


async def get_token(for_user: str) -> str:
    return await redis.get(f'token:{for_user}')


async def set_user_tz_val(tz_val: str | int, for_user: str):
    await redis.set(f'tz:{for_user}', str(tz_val))


async def set_user_token(token: str, for_user: str):
    await redis.set(f'token:{for_user}', token)
