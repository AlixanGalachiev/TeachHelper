from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Boolean, String, Enum
import enum

from .base import Base

class RoleUser(str, enum.Enum):
    teacher = "teacher"
    student = "student"
    admin   = "admin"


class Users(Base):
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[RoleUser] = mapped_column(Enum(RoleUser), nullable=False)
    is_verificated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
  