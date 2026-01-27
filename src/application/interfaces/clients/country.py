from typing import Protocol


class CountryClientInterface(Protocol):
    def get_country_code_by_name(self, country_name: str) -> str: ...
