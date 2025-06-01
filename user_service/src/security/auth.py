from fastapi.security import OAuth2PasswordBearer, OAuth2
from fastapi.requests import Request
from fastapi import HTTPException, Depends, status, Cookie

from schemas import LoginSchema

from sqlalchemy.exc import NoResultFound
from datetime import datetime, timezone, timedelta

import jwt

from dependencies import db_socket_dependency

from service.service import DBSocket

from models.models import User

from typing import Optional

import config


def encode(payload: dict) -> str:
    """setup and return encoded jwt token"""
    print(config.SECRET_KEY)
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


async def login_user(login_data: LoginSchema, socket: DBSocket = Depends(db_socket_dependency(User))):
    email, password = login_data.email, login_data.password
    user = await socket.get_db_obj(User.email == email)
    if not user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, {
                            'error': 'user with this email not found'})
    if not user.check_password(password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            {'error': 'wrong password'})
    return user


def extract_token(authorization_header: str):
    if not authorization_header:
        raise HTTPException(status.HTTP_403_FORBIDDEN, {
                            'error': 'authentication header was not provide'})
    if not authorization_header.startswith('Bearer '):
        raise HTTPException(status.HTTP_403_FORBIDDEN, {
                            'error': 'authentication header is incorrectly'})
    return authorization_header.split()[1]


class Auther:
    """base class for classes providing methods for authentication by token"""

    def __init__(self, socket: DBSocket):
        self.socket = socket

    async def auth(self, request: Request) -> User:
        pass

    def extract_payload(self, token: str, token_type: str) -> Optional[dict]:
        pass

    async def get_user(self, payload: dict, socket: DBSocket) -> User:
        pass


class JWTAuther(Auther):
    async def auth(self, token: str) -> User:
        payload = self.extract_payload(token)
        user = await self.get_user(payload)
        return user

    def extract_payload(self, token: str, token_type: str = 'access') -> Optional[dict]:
        try:
            payload = decode(token)
        except jwt.InvalidTokenError as err:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={
                                'error': str(err)})
        got_type = payload.get('type', None)
        if got_type != token_type:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={
                                'error': 'Wrong token type'})
        return payload

    async def get_user(self, payload: dict):
        user_id = payload.get('user_id', None)
        if not user_id:
            raise Exception(
                {'error': 'user_id was never set in token payload'})
        try:
            user = await self.socket.get_db_obj(User.id == user_id)
        except NoResultFound:
            raise Exception(
                {'error': 'Not existing user_id was set in token payload. Security threat!'})
        return user
