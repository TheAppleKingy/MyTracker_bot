from typing import Protocol, Optional


class CountryClientInterface(Protocol):
    def get_country_code_by_name(self, country_name: str) -> Optional[str]: ...
