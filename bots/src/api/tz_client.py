import httpx

import config

from .exc import TimezoneAPIError


async def get_country_timezones(country_code: str) -> list[str]:
    response = await httpx.AsyncClient().get(url='https://api.timezonedb.com/v2.1/list-time-zone', params={'key': config.TIMEZONE_DB_API_KEY, 'format': 'json', 'country': country_code})
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise TimezoneAPIError()
    return [country_info['zoneName'] for country_info in response.json()['zones']]
