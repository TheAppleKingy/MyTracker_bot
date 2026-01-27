from pycountry import countries

from src.application.interfaces.clients import CountryClientInterface
from .errors import InvalidCountryNameError


class CountryClient(CountryClientInterface):
    def get_country_code_by_name(self, country_name: str) -> str:
        try:
            results = countries.search_fuzzy(country_name)
        except LookupError:
            raise InvalidCountryNameError("Invalid country name. Try again", kb=None)
        if len(results) != 1:
            raise InvalidCountryNameError("Invalid country name. Try again", kb=None)
        return results[0].alpha_2
