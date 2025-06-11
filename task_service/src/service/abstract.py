from typing import TypeVar, Sequence

from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.expression import ColumnElement

from repository.socket import Socket


T = TypeVar('T')


class Service:
    _target_model: T

    def __init__(self, socket: Socket):
        assert socket.model is self._target_model, f'try to init {self.__class__.__name__} with inappropriate model in socket. got model: {socket.model}'
        self.socket = socket

    async def get_obj(self, *conditions: ColumnElement[bool], raise_exception: bool = False) -> T:
        pass

    async def get_objs(self, *conditions: ColumnElement[bool]) -> list[T]:
        pass

    async def get_column_vals(self, field: InstrumentedAttribute, *conditions: ColumnElement[bool]):
        pass

    async def get_columns_vals(self, fields: Sequence[InstrumentedAttribute], *conditions: ColumnElement[bool]):
        pass

    async def delete(self, *conditions: ColumnElement[bool]):
        pass

    async def update(self, *conditions: ColumnElement[bool], **kwargs):
        pass

    async def create_obj(self, **kwargs) -> T:
        pass

    async def create_objs(self, table_raws: Sequence[dict]) -> list[T]:
        pass


def extract_field(model: T, field_name: str) -> InstrumentedAttribute:
    field = getattr(model, field_name, None)
    if not field:
        raise AttributeError(
            {'error': f'Model {model} has no field with name "{field_name}"'})
    return field


async def m2m_validator(objects_data: list[dict], socket: Socket, identificator: str = 'id'):
    values = [data[identificator] for data in objects_data]

    if len(values) == len(set(values)):
        model = socket.model
        field = extract_field(model, identificator)
        identificators_vals = await socket.get_column_vals(field, field.in_(values))
        if len(identificators_vals) != len(values):
            existing_values = set(identificators_vals)
            missing_values = set(values) - existing_values
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f'Theese {identificator}s: ({", ".join(missing_values)}) - do not exist')
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'{identificator}s must be unique')

    return identificators_vals
