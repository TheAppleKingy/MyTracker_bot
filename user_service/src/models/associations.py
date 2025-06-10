from .base import Base

from sqlalchemy import ForeignKey, Column, Table


users_groups = Table(
    'users_groups',
    Base.metadata,
    Column('user_id', ForeignKey(
        'users.id', ondelete='CASCADE'), primary_key=True),
    Column('group_id', ForeignKey('groups.id',
           ondelete='CASCADE'), primary_key=True)
)
