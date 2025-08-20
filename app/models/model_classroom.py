import uuid
from sqlalchemy.dialects.postgresql import UUID
from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, UniqueConstraint

from . import Base


class Classroom(Base):
    __tablename__ = "classroom"

    name: Mapped[str] = mapped_column(String(200))
    teacher_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), index=True)

    teacher: Mapped["User"] = relationship(back_populates="taught_classes")
    students: Mapped[List["User"]] = relationship(
        secondary="classroomstudent",
        back_populates="classes",
    )

    __table_args__ = (
        UniqueConstraint("name", "teacher_id", name="uq_classroom_name_teacher"),
    )


class ClassroomStudent(Base):
    __tablename__ = "classroomstudent"
    classroom_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),  ForeignKey("classroom.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),  ForeignKey("user.id", ondelete="CASCADE"), index=True)
