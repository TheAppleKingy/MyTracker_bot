from typing import TypeVar, Sequence, Any, Callable, Generic

from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.expression import ColumnElement
from repository.socket import Socket
from .exceptions import db_exception_handler


T = TypeVar('T')


class Service(Generic[T]):
    _target_model: T

    def __init__(self, socket: Socket[T]):
        assert socket.model is self._target_model, f'try to init {self.__class__.__name__} with inappropriate model in socket. got model: {socket.model}'
        self.socket = socket

    @db_exception_handler
    async def get_obj(self, *conditions: ColumnElement[bool], raise_exception: bool = False):
        return await self.socket.get_db_obj(*conditions, raise_exception=raise_exception)

    @db_exception_handler
    async def get_objs(self, *conditions: ColumnElement[bool]) -> list[T]:
        return await self.socket.get_db_objs(*conditions)

    @db_exception_handler
    async def get_column_vals(self, field: InstrumentedAttribute, *conditions: ColumnElement[bool]):
        return await self.socket.get_column_vals(field, *conditions)

    @db_exception_handler
    async def get_columns_vals(self, fields: Sequence[InstrumentedAttribute], *conditions: ColumnElement[bool], mapped: bool = False):
        return await self.socket.get_columns_vals(fields, *conditions, mapped=mapped)

    @db_exception_handler
    async def delete(self, *conditions: ColumnElement[bool], commit: bool = True) -> list[T]:
        return await self.socket.delete_db_objs(*conditions, commit=commit)

    @db_exception_handler
    async def update(self, *conditions: ColumnElement[bool], commit: bool = True, **kwargs) -> list[T]:
        return await self.socket.update_db_objs(*conditions, commit=commit, **kwargs)

    @db_exception_handler
    async def create_obj(self, commit: bool = True, **kwargs) -> T:
        return await self.socket.create_db_obj(commit=commit, **kwargs)

    @db_exception_handler
    async def create_objs(self, table_raws: Sequence[dict], commit: bool = True) -> list[T]:
        return await self.socket.create_db_objs(table_raws, commit=commit)


def extract_field(model: T, field_name: str) -> InstrumentedAttribute:
    field = getattr(model, field_name, None)
    if not field:
        raise AttributeError(
            {'error': f'Model {model} has no field with name "{field_name}"'})
    return field


def extract_service_method(service: Service, method_name: str) -> Callable:
    method = getattr(service, method_name, None)
    if not method:
        raise AttributeError(
            {'error': f'Service {service} has no method with name "{method_name}"'})
    return method


async def check_objs_exist(objs_data: list[Any], objs_service: Service[T], identificator: str = 'id'):
    model = objs_service.socket.model
    id_field = extract_field(model, identificator)
    objs = await objs_service.get_objs(id_field.in_(objs_data))
    if len(objs) != len(objs_data):
        existing = {getattr(obj, identificator) for obj in objs}
        not_existing = list(map(str, set(objs_data) - existing))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'"{model.__name__}" objects with next "{identificator}"s do not exist: {','.join(not_existing)}')
    return objs


def check_is_object_field(obj: T, field: InstrumentedAttribute):
    model = obj.__class__
    if model is not field.class_:
        raise AttributeError(
            f'Obj is instance of "{model.__name__}", but got field "{field.key}" of "{field.class_.__name__}"')


def check_is_relationship(field: InstrumentedAttribute):
    field_name = field.key
    model = field.class_
    if not field_name in model.__mapper__.relationships.keys():
        raise AttributeError(
            f'Field "{field_name}" is not related with "{model.__name__}"')
    return field_name


def add_related_objs(obj: T, objs_to_add: Sequence[T], relation_field: InstrumentedAttribute):
    check_is_object_field(obj, relation_field)
    related_field_name = check_is_relationship(relation_field)
    related_objs = getattr(obj, related_field_name)
    added = []
    for obj in objs_to_add:
        if not obj in related_objs:
            related_objs.append(obj)
            added.append(obj)
    setattr(obj, related_field_name, related_objs)
    return added


def exclude_related_objs(obj: T, objs_to_exclude: Sequence[T], relation_field: InstrumentedAttribute):
    check_is_object_field(obj, relation_field)
    related_field_name = check_is_relationship(relation_field)
    related_objs = getattr(obj, related_field_name)
    excluded = []
    for obj in objs_to_exclude:
        if obj in related_objs:
            idx = related_objs.index(obj)
            del related_objs[idx]
            excluded.append(obj)
    setattr(obj, related_field_name, related_objs)
    return excluded


def get_difference(objs_list1: Sequence[T], objs_list2: Sequence[T]):
    if len(objs_list1) > len(objs_list2):
        res = set(objs_list1) - set(objs_list2)
    else:
        res = set(objs_list2) - set(objs_list1)
    return list(res)
