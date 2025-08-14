from typing import Optional, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text, Integer

from . import Base


class HomeworkStatus(str):
    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"


class Homework(Base):
    student_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True)
    classroom_id: Mapped[int] = mapped_column(ForeignKey("classroom.id", ondelete="SET NULL"), nullable=True, index=True)

    # исходники
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    recognized_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String(32), default=HomeworkStatus.PENDING)

    student: Mapped["User"] = relationship(back_populates="homeworks")
    classroom: Mapped["Classroom"] = relationship()
    errors: Mapped[List["ErrorItem"]] = relationship(back_populates="homework", cascade="all,delete-orphan")


class ErrorItem(Base):
    __tablename__ = "erroritem"

    homework_id: Mapped[int] = mapped_column(ForeignKey("homework.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(64))  # spelling, punctuation, grammar, ...
    message: Mapped[str] = mapped_column(String(500))
    start_pos: Mapped[int] = mapped_column(Integer)
    end_pos: Mapped[int] = mapped_column(Integer)

    homework: Mapped["Homework"] = relationship(back_populates="errors")
