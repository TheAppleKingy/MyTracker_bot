import httpx

from datetime import timezone, timedelta

from src.application.interfaces.clients import TimezoneClientInterface


class HttpTZClient(TimezoneClientInterface):
    def __init__(self, key: str, url: str):
        self._key = key
        self._url = url

    async def get_country_tz_offsets_minutes(self, country_code: str) -> list[int]:
        client = httpx.AsyncClient()
        resp = await client.get(self._url, params={"key": self._key, "format": "json", "country": country_code})
        if resp.status_code != 200:
            pass
        offsets = set()
        for zone_data in resp.json()["zones"]:
            offsets.add(zone_data["gmtOffset"])
        return [offset // 60 for offset in sorted(offsets)]
