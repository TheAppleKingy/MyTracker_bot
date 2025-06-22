import pytest
import pytest_asyncio

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from models.tasks import Task
from models.users import User
from service.task_service import TaskService


@pytest_asyncio.fixture
async def root(session: AsyncSession, task_service: TaskService, simple_user: User):
    root = await task_service.create_obj(title='root', description='root descr', user_id=simple_user.id)
    subroot1 = await task_service.create_obj(title='subroot1', description='subroot1 descr', task_id=root.id, user_id=simple_user.id)
    subsubroot1 = await task_service.create_obj(title='subsubroot1', description='subsubroot1 descr', task_id=subroot1.id, user_id=simple_user.id)
    subroot2 = await task_service.create_obj(title='subroot2', description='subroot2 descr', task_id=root.id, user_id=simple_user.id)
    await session.refresh(simple_user, ['tasks'])
    await session.refresh(root, ['subtasks'])
    await session.refresh(subroot1, ['subtasks'])
    return root
