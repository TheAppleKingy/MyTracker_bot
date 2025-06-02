from models.models import User, Group, users_groups

from fastapi import HTTPException, status

from service.service import DBSocket

from sqlalchemy.exc import NoResultFound


class BasePermission:
    def __init__(self, socket: DBSocket):
        self.socket = socket

    def check(user) -> User:
        """this method checks that user is allowed and return user obj otherwise raise HTTP_403_FORBIDDEN"""
        pass


class GroupPermission(BasePermission):
    def __init__(self, allowed_group: str, socket: DBSocket):
        super().__init__(socket)
        self.group = allowed_group

    async def check(self, user: User) -> User:
        group_obj = await self.get_group_obj()
        user_groups = user.groups
        if not group_obj in user_groups:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={
                                'error': 'you have no permissions'})
        return user

    async def get_group_obj(self) -> Group:
        try:
            group_obj = await self.socket.get_db_obj(Group.title == self.group)
        except NoResultFound as err:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=str(err))
        return group_obj
