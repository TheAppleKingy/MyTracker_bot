import httpx

from datetime import timezone

from application.interfaces.clients import TimezoneClientInterface


class HttpTZClient(TimezoneClientInterface):
    def __init__(self, key: str, url: str):
        self._key = key
        self._url = url
