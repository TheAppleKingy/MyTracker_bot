import jwt
import time

from src.application.interfaces.token_service import TokenServiceInterface


class JWTService(TokenServiceInterface):
    def __init__(self, secret: str):
        self._secret = secret

    def generate_token(self, tg_name: str) -> str:
        return jwt.encode({"tg_name": tg_name, "exp": int(time.time() + 5)}, self._secret, "HS256")
