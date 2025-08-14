from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Enum
import enum

from .base import Base


class Role(str, enum.Enum):
    teacher = "teacher"
    student = "student"


class User(Base):
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.student)
    # Пароль хранить в хэше, поле для примера
    password_hash: Mapped[str] = mapped_column(String(255))

    # связи
    taught_classes: Mapped[List["Classroom"]] = relationship(back_populates="teacher", cascade="all,delete-orphan")
    classes: Mapped[List["Classroom"]] = relationship(
        secondary="classroomstudent",
        back_populates="students"
    )
    homeworks: Mapped[List["Homework"]] = relationship(back_populates="student")
