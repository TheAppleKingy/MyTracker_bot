from .exc import BackendError, NotAuthenticatedError

from httpx import Response


class BackendResponse:
    def __init__(self, api_response: Response):
        self._response = api_response
        self.status = api_response.status_code
        if self.status >= 500:
            raise BackendError(self._response.text)
        if self.status == 401:
            raise NotAuthenticatedError()
        if self.status >= 400:
            msg = api_response.json().get('detail')
            raise BackendError(msg)

    @property
    def json(self) -> dict:
        return self._response.json()
