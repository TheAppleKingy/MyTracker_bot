from datetime import datetime, timezone
from typing import Optional, Literal

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.domain.entities import Task
from .shared import _main_button, _back_button, _next_button, _prev_button


def _task_info_button(task: Task):
    return types.InlineKeyboardButton(text=task.title, callback_data=f"get_task_{task.id}")


def _add_subtask_button(parent_id: int):
    return types.InlineKeyboardButton(text="Add subtask", callback_data=f'create_subtask_{parent_id}')


def _delete_task_button(task_id: int, parent_id: Optional[int] = None):
    return types.InlineKeyboardButton(text="Delete", callback_data=f'delete_task_{task_id}_{parent_id}')


def _update_task_button(task_id: int):
    return types.InlineKeyboardButton(text="Update", callback_data=f'update_task_{task_id}')


def _add_reminder_button(task_id: int):
    return types.InlineKeyboardButton(text="Add reminder", callback_data=f'add_reminder_{task_id}')


def _finish_task_button(task_id: int):
    return types.InlineKeyboardButton(text="Finish", callback_data=f"finish_task_{task_id}")


def _subtasks_button(parent_id: int, status: Literal["active", "finished"], page: int):
    return types.InlineKeyboardButton(text=f"{status.capitalize()} subtasks", callback_data=f"get_subtasks_{status}_{parent_id}_{page}")


def page_tasks_kb(
    tasks: list[Task],
    status: Literal["active", "finished"],
    prev_page: int = 0,
    next_page: int = 0,
    parent_id: Optional[int] = None
):
    builder = InlineKeyboardBuilder()
    task_buttons = [_task_info_button(task) for task in tasks]
    additional = []
    if prev_page:
        additional.append(
            _prev_button(
                f"get_tasks_{status}_{prev_page}_fromnavigation" if not parent_id else f"get_subtasks_{status}_{parent_id}_{prev_page}_fromnavigation"
            )
        )
    if parent_id:
        additional.append(_back_button(f"get_task_{parent_id}"))
    else:
        additional.append(_back_button("main_page"))
    if next_page:
        additional.append(
            _next_button(
                f"get_tasks_{status}_{next_page}_fromnavigation" if not parent_id else f"get_subtasks_{status}_{parent_id}_{next_page}_fromnavigation"
            )
        )
    builder.add(*task_buttons)
    builder.adjust(*[1]*len(tasks))
    builder.row(*additional)
    return builder.as_markup()


def no_tasks_kb():
    builder = InlineKeyboardBuilder()
    builder.add(_back_button("main_page"))
    builder.adjust(1, 1)
    return builder.as_markup()


def no_subtasks_kb(parent_id: int):
    builder = InlineKeyboardBuilder()
    builder.add(_back_button(f"get_task_{parent_id}"))
    builder.adjust(1)
    return builder.as_markup()


def _to_parent_button(parent_id: int):
    return types.InlineKeyboardButton(text="To parent", callback_data=f"get_task_{parent_id}")


def under_task_info_kb(task: Task):
    builder = InlineKeyboardBuilder()
    buttons = [
        _subtasks_button(task.id, "finished", 1),
    ]
    if not task.pass_date:
        buttons = [_subtasks_button(task.id, "active", 1), buttons[0]]
        buttons.extend([
            _update_task_button(task.id),
            _add_reminder_button(task.id),
            _add_subtask_button(task.id),
            _finish_task_button(task.id)
        ])
    buttons.append(_delete_task_button(task.id, task.parent_id))
    builder.add(*buttons)
    builder.adjust(2)
    builder.row(_to_parent_button(task.parent_id) if task.parent_id else _main_button())
    return builder.as_markup()


def update_task_terms_kb(task_id: int):
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(text="Title", callback_data=f"update_text_title"),
        types.InlineKeyboardButton(text="Description", callback_data=f"update_text_description"),
        types.InlineKeyboardButton(text="Deadline", callback_data=f"update_deadline"),
        _back_button(f"get_task_{task_id}")
    )
    builder.adjust(1)
    return builder.as_markup()
