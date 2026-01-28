from datetime import datetime, timezone
from typing import Optional, Literal

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.domain.entities import Task
from .shared import _main_button, _back_button


def _task_info_button(task: Task):
    return types.InlineKeyboardButton(text=task.title, callback_data=f"get_task_{task.id}")


def _subtasks_button(parent_id: int):
    return types.InlineKeyboardButton(text="Subtasks", callback_data=f"get_subtasks_{parent_id}")


def _add_subtask_button(parent_id: int):
    return types.InlineKeyboardButton(text="Add subtask", callback_data=f'create_subtask_{parent_id}')


def _create_task_button():
    return types.InlineKeyboardButton(text="Create task", callback_data='create_task')


def _delete_task_button(task_id: int):
    return types.InlineKeyboardButton(text="Delete", callback_data=f'delete_task_{task_id}')


def _update_task_button(task_id: int):
    return types.InlineKeyboardButton(text="Update", callback_data=f'update_task_{task_id}')


def _add_reminder_button(task_id: int):
    return types.InlineKeyboardButton(text="Add reminder", callback_data=f'add_reminder_{task_id}')


def _task_buttons_builder(tasks: list[Task], page: int, size: int):
    builder = InlineKeyboardBuilder()
    for task in tasks:
        builder.add(_task_info_button(task))
    return builder


def _next_active_task_page_button(page: int):
    return types.InlineKeyboardButton(text=">", callback_data=f"get_active_task_page_{page}")


def _prev_active_task_page_button(page: int):
    return types.InlineKeyboardButton(text="<", callback_data=f"get_active_task_page_{page}")


def tasks_kb(tasks: list[Task], additional_buttons: list[types.InlineKeyboardButton]):
    builder = _task_buttons_builder(tasks)
    for add in additional_buttons:
        builder.add(add)
    additional_size = [2]*(len(additional_buttons)//2)
    if len(additional_buttons) % 2:
        additional_size.append(1)
    sizes = [*additional_size] if not tasks else [
        *[1]*len(tasks), *additional_size]
    builder.adjust(*sizes)
    return builder.as_markup()


def page_tasks_kb(tasks: list[Task], prev_page: Optional[int] = None, next_page: Optional[int] = None):
    builder = InlineKeyboardBuilder()
    task_buttons = [_task_info_button(task) for task in tasks]
    navigations = []
    if prev_page:
        navigations.append(_prev_active_task_page_button(prev_page))
    if next_page:
        navigations.append(_next_active_task_page_button(next_page))
    builder.add(*task_buttons)
    builder.adjust(*[1]*len(tasks))
    if navigations:
        builder.row(*navigations)
    builder.row(_create_task_button())
    builder.row(_main_button())
    return builder.as_markup()


def no_tasks_kb():
    builder = InlineKeyboardBuilder()
    builder.add(_create_task_button(), _main_button())
    return builder.as_markup()


def under_task_info_kb(task: Task):
    builder = InlineKeyboardBuilder()
    builder.add(
        _subtasks_button(task.id),
        _delete_task_button(task.id),
        _update_task_button(task.id),
        _add_reminder_button(task.id),
        _add_subtask_button(task.id)
    )
    return builder.as_markup()
