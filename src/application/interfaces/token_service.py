from typing import Protocol, Optional


class TokenServiceInterface(Protocol):
    def generate_token(self, tg_name: str) -> str: ...
