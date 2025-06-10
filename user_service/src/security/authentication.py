from fastapi import HTTPException, Depends, status

from schemas import LoginSchema

from sqlalchemy.exc import NoResultFound
from datetime import datetime, timezone, timedelta

import jwt

from dependencies import get_socket, get_user_service

from repository.socket import Socket
from service.user_service import UserService

from models.models import User

from typing import Optional, Literal

import config


def encode(payload: dict):
    """setup and return encoded jwt token"""
    token = jwt.encode(payload, config.SECRET_KEY)
    return token


def decode(token: str) -> dict:
    """return decoded jwt token"""
    payload = jwt.decode(token, config.SECRET_KEY, algorithms=['HS256'])
    return payload


def refresh(payload: dict):
    """setup and return refresh token"""
    payload.update({'type': 'refresh', 'exp': datetime.now(
        timezone.utc) + timedelta(seconds=int(config.REFRESH_EXPIRE_TIME))})
    refresh = encode(payload)
    return refresh


def access(payload: dict):
    """setup and return access token"""
    payload.update({'type': 'access', 'exp': datetime.now(
        timezone.utc) + timedelta(seconds=int(config.ACCESS_EXPIRE_TIME))})
    access = encode(payload)
    return access


def validate_token(token: Optional[str], fields_required: Optional[list[str]] = None) -> dict:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={
                            'error': 'token was not provide'})
    try:
        decoded = decode(token)
    except jwt.InvalidTokenError as err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={
                            'error': str(err)})
    if fields_required:
        if not all([key in decoded.keys() for key in fields_required]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={
                                'error': 'provided token do not contain required info'})
    return decoded


def get_tokens_for_user(user: User):
    payload = {'user_id': user.id}
    access_token = access(payload)
    refresh_token = refresh(payload)
    return access_token, refresh_token


async def login_user(login_data: LoginSchema, user_service: UserService = Depends(get_user_service)) -> User:
    email, password = login_data.email, login_data.password
    user = await user_service.get_user(User.email == email)
    if not user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, {
                            'error': 'user with this email not found'})
    if not user.check_password(password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            {'error': 'wrong password'})
    return user


class Auther:
    """base class for classes providing methods for authentication by token"""

    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def auth(self, token: str) -> User:
        pass

    def extract_payload(self, token: str) -> Optional[dict]:
        pass

    async def get_user(self, decoded_token: dict) -> User:
        pass


class JWTAuther(Auther):
    async def auth(self, token: str, token_type: Literal['refresh', 'access']) -> User:
        payload = self.extract_payload(token, token_type)
        user = await self.get_user(payload)
        return user

    def extract_payload(self, token: Optional[str], required_type: str) -> Optional[dict]:
        payload = validate_token(token, ['user_id', 'type'])
        got_type = payload['type']
        if got_type != required_type:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={
                                'error': 'Wrong token type'})
        return payload

    async def get_user(self, decoded_token: dict):
        user_id = decoded_token['user_id']
        try:
            user = await self.user_service.get_user(User.id == user_id, raise_exception=True)
        except NoResultFound:
            raise Exception(
                {'error': 'Not existing user_id was set in token payload. Security threat!'})
        return user
