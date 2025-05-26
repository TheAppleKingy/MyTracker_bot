from .users import User

from service.utils import M2MFactory

from . import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Table, Column, ForeignKey


class Task(Base):
    __tablename__ = 'tasks'
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(nullable=False, unique=True)
