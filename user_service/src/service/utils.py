from datetime import date, datetime

from functools import lru_cache

from typing import Any, Iterable, TypeVar

from sqlalchemy import Integer, String, Integer, Float, Boolean, Date, DateTime, Numeric, Text, SmallInteger, Table, Column, ForeignKey

from models import Base


T = TypeVar('T')


class QueryFilterBuilder:
    conditions_mapping = {
        'eq': lambda f, v: f == v,
        'ne': lambda f, v: f != v,
        'gte': lambda f, v: f >= v,
        'lte': lambda f, v: f <= v,
        'gt': lambda f, v: f > v,
        'lt': lambda f, v: f < v,
        'in': lambda f, v: f.in_(v),
        'not_in': lambda f, v: ~f.in_(v),
        'like': lambda f, v: f.like(v),
        'ilike': lambda f, v: f.ilike(v),
        'is': lambda f, _: f.is_(None),
        'is_not': lambda f, _: f.is_not(None),
        'between': lambda f, v: f.between(v[0], v[1]),
        'contains': lambda f, v: f.contains(v),
        'startswith': lambda f, v: f.startswith(v),
        'endswith': lambda f, v: f.endswith(v),
    }

    types_supported_by_suffixes: dict[str, tuple] = {
        'eq': (int, float, str, datetime, date, bool, ),
        'ne': (int, float, str, datetime, date, bool, ),
        'gte': (int, float, datetime, date, ),
        'lte': (int, float, datetime, date, ),
        'gt': (int, float, datetime, date, ),
        'lt': (int, float, datetime, date, ),
        'like': (str, ),
        'ilike': (str, ),
        'contains': (str, ),
        'startswith': (str, ),
        'endswith': (str, ),
        'in': (list, tuple, set, ),
        'not_in': (list, tuple, set, ),
        'between': (tuple, list, ),
        'is': (type(None), ),
        'is_not': (type(None), )
    }

    def __init__(self, model: T):
        self.__model = model

    @lru_cache(maxsize=128)
    def __get_python_type(self, param: tuple[str]) -> tuple[type]:
        """Compares sqlalchemy type and python type"""
        field_name = param[0]
        field = getattr(self.__model, field_name)
        column_type = field.property.columns[0].type
        is_nullable = field.property.columns[0].nullable
        if isinstance(column_type, (String, Text)):
            python_type = (str, )
        elif isinstance(column_type, (Integer, SmallInteger)):
            python_type = (int, )
        elif isinstance(column_type, (Float, Numeric)):
            python_type = (float, )
        elif isinstance(column_type, Boolean):
            python_type = (bool, )
        elif isinstance(column_type, (Date, DateTime)):
            python_type = (datetime, )
        else:
            python_type = (Any, )
        if is_nullable:
            python_type += (type(None), )
        return python_type

    def get_prepaired_data(self, data: dict[str, Any]):
        prepaired_data = dict()
        for k, v in data.items():
            parsed_key = tuple(k.split('__'))
            if len(parsed_key) == 1:
                parsed_key += ('eq', )
            prepaired_data.update({parsed_key: v})
        return prepaired_data

    @lru_cache(maxsize=128)
    def get_condition_map(self, cond: str) -> str:
        return self.conditions_mapping[cond]

    @lru_cache(maxsize=128)
    def get_supported_types_for_suffix(self, suffix: str):
        return self.types_supported_by_suffixes[suffix]

    def compare_got_type_and_field(self, param: tuple[str], value):
        python_types = self.__get_python_type(param)
        if issubclass(type(value), Iterable):
            type_seq = list({type(v) for v in value})
            if len(type_seq) != 1:
                raise TypeError(f'Got different types in "{'__'.join(param)}"')
            if python_types[0] != type_seq[0]:
                raise TypeError(
                    f'Got {type_seq[0]} type of values are not comparable with "{param[0]}" field type, must be {python_types}')
            return
        if not type(value) in python_types:
            raise TypeError(
                f'Cannot use {type(value)} type for "{param[0]}" field, type must be in {python_types}')

    def validate_value(self, param: tuple[str], value):
        python_types = self.__get_python_type(param)
        print(python_types)
        if type(value) not in python_types:
            raise TypeError(
                f'Parameter "{'__'.join(param)}" got unexpected type: {type(value)}, must be {python_types}')

    def check_suffix_support_type(self, param: tuple[str], value):
        suffix = param[1]
        supported_types = self.get_supported_types_for_suffix(suffix)
        if not type(value) in supported_types:
            raise TypeError(f'Cannot use __{suffix} for {type(value)} type')

    def check_suffix(self, param: tuple[str]):
        suffix = param[1]
        if not suffix in self.conditions_mapping:
            raise KeyError(
                f'Used wrong suffix: {suffix}')

    def check_model_has_field(self, param: tuple[str]):
        field_name = param[0]
        if not hasattr(self.__model, field_name):
            raise AttributeError(
                f'Model {self.__model} has no field "{field_name}"')

    def check_param_alias(self, param):
        self.check_model_has_field(param)
        self.check_suffix(param)

    def check_args(self, prepaired_data: dict[tuple[str], Any]):
        for param, value in prepaired_data.items():
            self.check_param_alias(param)
            self.check_suffix_support_type(param, value)
            self.compare_got_type_and_field(param, value)

    def build(self, **data) -> tuple[bool]:
        """Generate arguments for and_(), or_(), not()_ or may by use for where()\n
           Does not support relations yet"""
        prepared_data = self.get_prepaired_data(data)
        param_cond_val = []
        self.check_args(prepared_data)
        for param, value in prepared_data.items():
            param_name, condition = param
            map_ = self.get_condition_map(condition)
            field = getattr(self.__model, param_name)
            param_cond_val.append(map_(field, value))
        return param_cond_val


class QueryFilterBuilderFabric:
    @classmethod
    def get_build(cls, model: T):
        return QueryFilterBuilder(model).build


class M2MBuilder:
    """This builder can build m2m table only by first pk in model attr list. Advise to define "id" in Base"""

    def __init__(self, model1: T, model2: T):
        self._model1 = model1
        self._model2 = model2
        self.__metadata = Base.metadata

    def get_tablename(self, by_model: int) -> str:
        model = getattr(self, f'_model{by_model}')
        if not (model.__tablename__.islower() and model.__tablename__.endswith('s')):
            raise ValueError(f'Tablename for model {model} is incorrect')
        return model.__tablename__

    def get_pk(self, by_model: int):
        model = getattr(self, f'_model{by_model}')
        for column in model.__table__.columns.values():
            if column.primary_key:
                return str(column)
        raise AttributeError(f'"{model.__tablename__}" has no pk')

    def build_m2m_name(self) -> str:
        name1 = self.get_tablename(1)
        name2 = self.get_tablename(2)
        return f'{name1}_{name2}'

    def get_single_name(self, for_model: int):
        tablename = self.get_tablename(for_model)
        return tablename.removesuffix('s')

    def get_fk_columns(self) -> list[Column]:
        pk1, pk2 = self.get_pk(1), self.get_pk(2)
        pk_name1, pk_name2 = pk1.split('.')[1], pk2.split('.')[1]
        single_name1, single_name2 = self.get_single_name(
            1), self.get_single_name(2)
        column_name1, column_name2 = f'{single_name1}_{pk_name1}', f'{single_name2}_{pk_name2}'
        return [Column(column_name1, ForeignKey(pk1), primary_key=True), Column(column_name2, ForeignKey(pk2), primary_key=True)]

    def build_m2m(self, *args: Column) -> Table:
        m2m_name = self.build_m2m_name()
        fk = self.get_fk_columns()
        m2m_table = Table(
            m2m_name,
            self.__metadata,
            *fk,
            *args
        )
        return m2m_table


class M2MFactory:
    @classmethod
    def get_m2m_table(cls, model1: T, model2: T):
        return M2MBuilder(model1, model2).build_m2m()
