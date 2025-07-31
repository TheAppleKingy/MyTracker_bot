from datetime import datetime, timezone
from typing import Optional, Literal

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram3_calendar import SimpleCalendar

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


def delete_task_button(task_id: int):
    return types.InlineKeyboardButton(text="Delete", callback_data=f'delete_task_{task_id}')


def update_task_button(task_id: int):
    return types.InlineKeyboardButton(
        text="Update", callback_data=f'update_task_{task_id}')


def back_button(to_id: int):
    return types.InlineKeyboardButton(
        text="Back", callback_data=f'get_task_{to_id}')


def add_reminder_button(for_id: int):
    return types.InlineKeyboardButton(
        text="Add reminder", callback_data=f'add_reminder_{for_id}')


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
    additional_size = [2]*(len(additional_buttons)//2)
    if len(additional_buttons) % 2:
        additional_size.append(1)
    sizes = [*additional_size] if not tasks else [
        *[1]*len(tasks), *additional_size]
    builder.adjust(*sizes)
    return builder.as_markup()


def root_list_kb(tasks: list[TaskViewSchema]):
    return tasks_kb(tasks, [create_task_button()])


def for_task_info_kb(task: TaskViewSchema):
    buttons = []
    if not bool(task.pass_date):
        buttons += [add_subtask_button(
            task.id), update_task_button(task.id), add_reminder_button(task.id)]
    if task.task_id:
        buttons.append(back_button(task.task_id))
    buttons.append(delete_task_button(task.id))
    buttons.append(my_tasks_button())
    return tasks_kb(task.subtasks, buttons)


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


async def kalendar_kb(year: Optional[int] = None, month: Optional[int] = None):
    if not year:
        year = datetime.now().year
    if not month:
        month = datetime.now().month
    return await SimpleCalendar.start_calendar(year, month)


def time_kb(time_of: str, action: Literal['set', 'update'] = 'set', from_hour: int = 0, to_hour: int = 24):
    """to_time value wil not be included in range!"""
    builder = InlineKeyboardBuilder()
    buttons = [
        types.InlineKeyboardButton(
            text=f"0{i}h:00m" if i < 9 else f"{i}h:00m",
            callback_data=f"{action}_{time_of}_hour_{i}"
        )
        for i in range(from_hour, to_hour)
    ]
    for i in range(0, len(buttons), 4):
        builder.row(*buttons[i:i+4])

    return builder.as_markup()


def deadline_time_kb(user_tz: timezone, selected_date: datetime, for_update: bool = False):
    current_datetime_local = datetime.now(timezone.utc).astimezone(user_tz)
    action = 'set'
    if for_update:
        action = 'update'
    if current_datetime_local.date() == selected_date.date():
        return time_kb('deadline', action, from_hour=current_datetime_local.hour + 1)
    if selected_date.date() > current_datetime_local.date():
        return time_kb('deadline', action)


def remind_time_kb(deadline_local: datetime, selected_date: datetime):
    user_tz = deadline_local.tzinfo
    current_datetime_local = datetime.now(timezone.utc).astimezone(user_tz)
    if deadline_local.date() == current_datetime_local.date():
        return time_kb('remind', from_hour=current_datetime_local.hour + 1, to_hour=deadline_local.hour)
    if deadline_local.date() > current_datetime_local.date():
        if current_datetime_local.date() == selected_date.date():
            return time_kb('remind', from_hour=current_datetime_local.hour + 1)
        if selected_date.date() == deadline_local.date():
            return time_kb('remind', to_hour=deadline_local.hour)
        return time_kb('remind')


def add_reminder_kb():
    builder = InlineKeyboardBuilder()
    builder.add(add_reminder_button())
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
