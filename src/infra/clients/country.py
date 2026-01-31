from typing import Optional

from pycountry import countries

from src.application.interfaces.clients import CountryClientInterface


class CountryClient(CountryClientInterface):
    def get_country_code_by_name(self, country_name: str) -> Optional[str]:
        try:
            results = countries.search_fuzzy(country_name)
        except LookupError:
            return None
        if len(results) != 1:
            return None
        return results[0].alpha_2  # type: ignore
