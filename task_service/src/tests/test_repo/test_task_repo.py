import pytest

from datetime import datetime, timezone

from infra.db.models.tasks import Task
from infra.db.repository.task_repo import TaskRepository
from infra.db.repository.exceptions import TaskRepositoryError


pytest_mark_asyncio = pytest.mark.asyncio


@pytest_mark_asyncio
async def test_get_nested(task1: Task, task_repo: TaskRepository):
    task = await task_repo.get_nested_tasks(task1.id)
    assert task == task1
    assert task.subtasks == task1.subtasks


@pytest_mark_asyncio
async def test_get_nested_list(task1: Task, task_repo: TaskRepository):
    tasks = await task_repo.get_nested_tasks(task1.id, return_list=True)
    assert tasks == [task1]+task1.subtasks


@pytest_mark_asyncio
async def test_get_nested_none(task_repo: TaskRepository):
    with pytest.raises(TaskRepositoryError):
        task = await task_repo.get_nested_tasks(0)


@pytest_mark_asyncio
async def test_get_nested_one(task1: Task, task_repo: TaskRepository):
    task = await task_repo.get_nested_tasks(task1.subtasks[0].id)
    assert task == task1.subtasks[0]


@pytest_mark_asyncio
async def test_finish_task(task1: Task, task_repo: TaskRepository):
    assert not task1.done
    finished = await task_repo.finish_task(task1)
    assert finished.id == task1.id
    assert task1.done


@pytest_mark_asyncio
async def test_finish_already_done(task1: Task, task_repo: TaskRepository):
    task1.pass_date = datetime.now(timezone.utc)
    task1.done = True
    with pytest.raises(TaskRepositoryError):
        await task_repo.finish_task(task1)
