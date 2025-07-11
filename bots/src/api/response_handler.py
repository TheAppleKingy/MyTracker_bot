from httpx import Response

from .exc import NotAuthenticatedError, BackendError


class BackendResponse:
    def __init__(self, api_response: Response):
        self._response = api_response
        self.status = api_response.status_code

    @property
    def json(self):
        if self.status < 400:
            return self._response.json()
        if self.status >= 500:
            raise BackendError(self._response.text)
        if self.status == 401:
            raise NotAuthenticatedError('You have to login')
        raise BackendError('\n'.join(self._response.json()['detail']['msgs']))
