import jwt

import config

from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import HTTPException, status

from infra.db.models.users import User


def encode(payload: dict):
    """setup and return encoded jwt token"""
    token = jwt.encode(payload, config.SECRET_KEY)
    return token


def decode(token: str) -> dict:
    """return decoded jwt token"""
    payload = jwt.decode(token, config.SECRET_KEY, algorithms=['HS256'])
    return payload


def get_token(payload: dict):
    """setup and return token"""
    payload.update({'exp': datetime.now(
        timezone.utc) + timedelta(seconds=int(config.TOKEN_EXPIRE_TIME))})
    token = encode(payload)
    return token


def validate_token(token: Optional[str] = None, fields_required: Optional[list[str]] = None) -> dict:
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


def get_token_for_user(user: User):
    payload = {'user_id': user.id}
    token = get_token(payload)
    return token
