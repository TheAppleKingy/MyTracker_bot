from .base import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from security import hash_password, check_password


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(
        unique=True, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_admin: Mapped[bool] = mapped_column(nullable=False)

    def set_password(self):
        self.password = hash_password(self.password)

    def check_password(self, verifiable: str):
        hashed_password = self.password
        return check_password(verifiable, hashed_password)
