from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from api.schemas import Task


def get_my_tasks_kb():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="My tasks", callback_data='get_task_all'))
    return builder.as_markup()


def add_subtask_kb():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Add subtask", callback_data='create_task'))
    return builder.as_markup()


def create_task_kb():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Create task", callback_data='create_task'))
    return builder.as_markup()


def update_task_kb():
    buillder = InlineKeyboardBuilder()
    buillder.add(types.InlineKeyboardButton(
        text="Update", callback_data='update_task'))
    return buillder.as_markup()


def back_kb():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Back", callback_data='back'))
    return builder.as_markup()


def task_buttons(tasks: list[Task]):
    builder = InlineKeyboardBuilder()
    for task in tasks:
        builder.add(types.InlineKeyboardButton(
            text=task.title[:15], callback_data=f'get_task_{task.id}'))
    return builder


def tasks_kb(tasks: list[Task], additional_buttons: list[types.InlineKeyboardButton] = []):
    builder = task_buttons(tasks)
    for add in additional_buttons:
        builder.add(add)
    sizes = [len(additional_buttons)] if not tasks else [
        len(tasks), len(additional_buttons)]
    builder.adjust(*sizes)
    return builder.as_markup()


def root_list_kb(tasks: list[Task]):
    return tasks_kb(tasks, [create_task_kb().inline_keyboard[0][0]])


def subtasks_list_kb(subtasks: list[Task]):
    return tasks_kb(subtasks, [add_subtask_kb().inline_keyboard[0][0], update_task_kb().inline_keyboard[0][0], back_kb().inline_keyboard[0][0]])
