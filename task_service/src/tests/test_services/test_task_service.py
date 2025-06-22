import pytest

from datetime import datetime, timezone

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, async_sessionmaker

from models.users import User
from models.tasks import Task
from service.task_service import TaskService
from service.user_service import UserService
from service.exceptions import ServiceError


pytest_mark_asyncio = pytest.mark.asyncio


@pytest_mark_asyncio
async def test_check_done(task_service: TaskService, root: Task):
    assert not task_service.check_task_done(root)
    with pytest.raises(ValueError):
        root.done = True
    root.pass_date = datetime.now(timezone.utc)
    root.done = True
    assert task_service.check_task_done(root)


@pytest_mark_asyncio
async def test_get_user_roots(simple_user: User, task_service: TaskService, root: Task):
    user_roots = task_service.get_root_tasks_for_user(simple_user)
    assert [root] == user_roots
    idx = simple_user.tasks.index(root)
    del simple_user.tasks[idx]
    assert task_service.get_root_tasks_for_user(simple_user) == []


@pytest_mark_asyncio
async def test_check_is_root_for_user(simple_user: User, root: Task, task_service: TaskService):
    assert not task_service.check_is_root_for_user(simple_user, root)
    root.task_id = 9
    with pytest.raises(ServiceError):
        task_service.check_is_root_for_user(simple_user, root)
    with pytest.raises(ServiceError):
        subroot = root.subtasks[0]
        task_service.check_is_root_for_user(simple_user, subroot)


@pytest_mark_asyncio
async def test_get_root_tasks(root: Task, task_service: TaskService):
    roots = await task_service.get_root_tasks()
    assert roots == [root]


@pytest_mark_asyncio
async def test_get_task_tree(root: Task, task_service: TaskService):
    nested_tasks = await task_service.get_task_tree(root, return_root=False)
    assert len(nested_tasks) == 4
    assert root in nested_tasks
    sub1, sub2 = root.subtasks
    subsub1 = sub1.subtasks[0]
    assert sub1 in nested_tasks
    assert sub2 in nested_tasks
    assert subsub1 in nested_tasks


@pytest_mark_asyncio
async def test_get_user_task_tree(simple_user: User, task_service: TaskService, root: Task):
    sub1 = root.subtasks[0]
    user_tree = await task_service.get_user_task_tree(simple_user, root)
    assert user_tree == root
    assert user_tree.subtasks == root.subtasks
    with pytest.raises(ServiceError):
        await task_service.get_user_task_tree(simple_user, sub1)


@pytest_mark_asyncio
async def test_finish_task(root: Task, task_service: TaskService):
    with pytest.raises(ServiceError):
        await task_service.finish_task(root)
    for sub in root.subtasks:
        for subsub in sub.subtasks:
            subsub.pass_date = datetime.now(timezone.utc)
            subsub.done = True
        sub.pass_date = datetime.now(timezone.utc)
        sub.done = True
    await task_service.socket.session.commit()
    finished = await task_service.finish_task(root)
    assert finished.id == root.id
    assert finished.done


@pytest_mark_asyncio
async def test_finish_user_task(root: Task, task_service: TaskService, simple_user: User, admin_user: User):
    admin_task = await task_service.create_obj(
        title='admin_task', description='opapa', user_id=admin_user.id)
    with pytest.raises(ServiceError):
        await task_service.finish_user_task(admin_user, root)
    finished = await task_service.finish_user_task(admin_user, admin_task)
    assert finished.id == admin_task.id
    assert finished.user == admin_user
    assert finished.done
