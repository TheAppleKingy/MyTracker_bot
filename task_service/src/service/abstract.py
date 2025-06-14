from typing import TypeVar, Sequence, Any, Callable, Generic

from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.expression import ColumnElement
from repository.socket import Socket


T = TypeVar('T')


class Service(Generic[T]):
    _target_model: T

    def __init__(self, socket: Socket[T]):
        assert socket.model is self._target_model, f'try to init {self.__class__.__name__} with inappropriate model in socket. got model: {socket.model}'
        self.socket = socket

    async def get_obj(self, *conditions: ColumnElement[bool], raise_exception: bool = False):
        return await self.socket.get_db_obj(*conditions, raise_exception=raise_exception)

    async def get_objs(self, *conditions: ColumnElement[bool]) -> list[T]:
        return await self.socket.get_db_objs(*conditions)

    async def get_column_vals(self, field: InstrumentedAttribute, *conditions: ColumnElement[bool]):
        return await self.socket.get_column_vals(field, *conditions)

    async def get_columns_vals(self, fields: Sequence[InstrumentedAttribute], *conditions: ColumnElement[bool]):
        return await self.socket.get_columns_vals(fields, *conditions)

    async def delete(self, *conditions: ColumnElement[bool], commit: bool = True) -> list[T]:
        return await self.socket.delete_db_objs(*conditions, commit=commit)

    async def update(self, *conditions: ColumnElement[bool], commit: bool = True, **kwargs) -> list[T]:
        return await self.socket.update_db_objs(*conditions, commit=commit, **kwargs)

    async def create_obj(self, commit: bool = True, **kwargs) -> T:
        return await self.socket.create_db_obj(commit=commit, **kwargs)

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


async def m2m_field_validator(objs_data_to_add: list[Any], service: Service[T], identificator: str = 'id'):
    """Use this func when u have to get objs for add to m2m relationship from got list of identificators from client"""
    model = service.socket.model
    id_field = extract_field(model, identificator)
    objs_to_add = await service.get_objs(id_field.in_(objs_data_to_add))
    if len(objs_to_add) != len(objs_data_to_add):
        existing = {getattr(obj, identificator) for obj in objs_to_add}
        not_existing = list(map(str, set(objs_data_to_add) - existing))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Trying add m2m objects with not existing {identificator}s: {','.join(not_existing)}')
    return objs_to_add
