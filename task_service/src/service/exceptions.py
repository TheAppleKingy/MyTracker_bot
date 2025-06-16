from typing import Callable

from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError


def parse_integrity_err_msg(msg: str):
    detail = msg.split('\n')[1].split(maxsplit=1)[1]
    return detail


def internal_exc_to_http(service_method: Callable):
    async def catch(self, *args, **kwargs):
        try:
            return await service_method(self, *args, **kwargs)
        except IntegrityError as err:
            msg = str(err)
            info = parse_integrity_err_msg(msg)
            raise ServiceError(info, err)
        except Exception as err:
            raise ServiceError(str(err), err)
    return catch


class ServiceError(HTTPException):
    def __init__(self, msg: str, err: Exception = None, headers=None, status_code=400):
        detail = {}
        if err:
            detail.update({'exception class': err.__class__.__name__})
        detail.update({'msgs': msg.split('\n')})
        super().__init__(status_code, detail, headers)
