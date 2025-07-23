from .exc import BackendError, NotAuthenticatedError, RegistrationError

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
            detail = api_response.json().get('detail')
            msg = detail.get('msgs')[0]
            raise BackendError(msg)

    @property
    def json(self):
        return self._response.json()
