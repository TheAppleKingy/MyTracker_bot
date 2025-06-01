from fastapi import APIRouter, Depends, status


token_rout = APIRouter(
    '/api/get_access',
    tags=['Token']
)


@token_rout.get('')
def get_access():
    pass
