class BackendError(Exception):
    pass


class NotAuthenticatedError(BackendError):
    pass


class NoTimezoneError(BackendError):
    pass


class RegistrationError(BackendError):
    pass
