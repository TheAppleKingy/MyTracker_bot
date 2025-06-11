from fastapi import HTTPException, status
from sqlalchemy.exc import NoResultFound

from service.group_service import GroupService
from models.users import User, Group


class BasePermission:
    def __init__(self, group_service: GroupService):
        self.group_service = group_service

    def check(user: User) -> User:
        """this method checks that user is allowed and return user obj otherwise raise HTTP_403_FORBIDDEN"""
        pass


class GroupPermission(BasePermission):
    def __init__(self, allowed_group: str, group_service: GroupService):
        self.group_service = group_service
        self.group = allowed_group

    async def check(self, user: User) -> User:
        group = await self.get_group_obj()
        user_groups = user.groups
        if not group in user_groups:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={
                                'error': 'you have no permissions'})
        return user

    async def get_group_obj(self) -> Group:
        try:
            group_obj = await self.group_service.get_group(Group.title == self.group, raise_exception=True)
        except NoResultFound as err:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=str(err))
        return group_obj
