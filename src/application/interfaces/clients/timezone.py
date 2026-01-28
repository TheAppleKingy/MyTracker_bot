from typing import Protocol


class TimezoneClientInterface(Protocol):
    async def get_country_tz_offsets_minutes(self, country_code: str) -> list[int]: ...
