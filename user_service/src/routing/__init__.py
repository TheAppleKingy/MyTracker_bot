from fastapi.responses import JSONResponse


from typing import Optional


def response_cookies(response_data: Optional[dict], status: Optional[int], cookies_data: Optional[dict] = None, delete: bool = False):
    response = JSONResponse(response_data, status)
    if cookies_data:
        if not delete:
            for key in cookies_data:
                response.set_cookie(
                    key=key, value=cookies_data[key])
        else:
            for key in cookies_data:
                response.delete_cookie(key=key)
    return response
