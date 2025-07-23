from datetime import datetime, timedelta, timezone
from typing import Optional

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram3_calendar import SimpleCalendar, simple_cal_callback

from api.schemas import TaskViewSchema


def my_tasks_button():
    return types.InlineKeyboardButton(
        text="My tasks", callback_data='get_task_all')


def add_subtask_button(for_task_id: int):
    return types.InlineKeyboardButton(
        text="Add subtask", callback_data=f'create_subtask_{for_task_id}')


def create_task_button():
    return types.InlineKeyboardButton(
        text="Create task", callback_data='create_task')


def update_task_button(task_id: int):
    return types.InlineKeyboardButton(
        text="Update", callback_data=f'update_task_{task_id}')


def back_button(to_id: int):
    return types.InlineKeyboardButton(
        text="Back", callback_data=f'get_task_{to_id}')


def get_my_tasks_kb():
    builder = InlineKeyboardBuilder()
    builder.add(my_tasks_button())
    return builder.as_markup()


def add_subtask_kb(for_task_id: int):
    builder = InlineKeyboardBuilder()
    builder.add(add_subtask_button(for_task_id))
    return builder.as_markup()


def create_task_kb():
    builder = InlineKeyboardBuilder()
    builder.add(create_task_button())
    return builder.as_markup()


def update_task_kb(task_id: int):
    buillder = InlineKeyboardBuilder()
    buillder.add(update_task_button(task_id))
    return buillder.as_markup()


def back_kb(to_id: int):
    builder = InlineKeyboardBuilder()
    builder.add(back_button(to_id))
    return builder.as_markup()


def task_buttons_builder(tasks: list[TaskViewSchema]):
    builder = InlineKeyboardBuilder()
    for task in tasks:
        builder.add(types.InlineKeyboardButton(
            text=task.title, callback_data=f'get_task_{task.id}'))
    return builder


def tasks_kb(tasks: list[TaskViewSchema], additional_buttons: list[types.InlineKeyboardButton]):
    builder = task_buttons_builder(tasks)
    for add in additional_buttons:
        builder.add(add)
    sizes = [len(additional_buttons)] if not tasks else [
        *[1]*len(tasks), len(additional_buttons)]
    builder.adjust(*sizes)
    return builder.as_markup()


def root_list_kb(tasks: list[TaskViewSchema]):
    return tasks_kb(tasks, [create_task_button()])


def for_task_info_kb(task: TaskViewSchema):
    additional_buttons = [add_subtask_button(
        task.id), update_task_button(task.id)]
    if task.task_id:
        additional_buttons.append(back_button(task.task_id))
    additional_buttons.append(my_tasks_button())
    return tasks_kb(task.subtasks, additional_buttons)


def for_task_update_kb(for_task_id: int):
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text='Change title', callback_data=f'change_title'),
        types.InlineKeyboardButton(
            text="Change description", callback_data=f'change_description'),
        types.InlineKeyboardButton(
            text="Change deadline", callback_data=f"change_deadline"),
        types.InlineKeyboardButton(
            text="Mark task as done", callback_data=f"mark_done_{for_task_id}"),
        back_button(for_task_id)
    )
    builder.adjust(*[1, 1, 1, 1, 1])
    return builder.as_markup()


async def kalendar_kb():
    calendar = SimpleCalendar()
    return await calendar.start_calendar()


def reminders_time_kb(deadline_hour: int):
    builder = InlineKeyboardBuilder()
    buttons = [
        types.InlineKeyboardButton(
            text=f"{i}",
            callback_data=f"set_remind_hour_{i}"
        )
        for i in range(1, deadline_hour)
    ]

    for i in range(0, len(buttons), 4):
        builder.row(*buttons[i:i+4])

    return builder.as_markup()


def add_reminder_kb():
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Add reminder", callback_data='add_reminder'),
    )
    return builder.as_markup()


def yes_or_no_kb(yes_callback_data: str = '', no_callback_data: str = ''):
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Yes", callback_data=yes_callback_data),
        types.InlineKeyboardButton(
            text="No", callback_data=no_callback_data),
    )
    return builder.as_markup()
