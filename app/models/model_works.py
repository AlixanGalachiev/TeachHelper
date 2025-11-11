from datetime import datetime
import enum
import uuid

from sqlalchemy import UUID, Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Table
from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

class StatusWork(str, enum.Enum):
    draft        = "draft"
    inProgress   = "inProgress"
    verification = "verification"
    verificated  = "verificated"
    canceled     = "canceled"

class Assessment(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    answer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("answers.id", ondelete="CASCADE"), nullable=False)
    e_criterion_id:  Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("e_criterions.id", ondelete="CASCADE"), nullable=False)
    points: Mapped[int] = mapped_column(Integer, default=False, nullable=False)


class Answers(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    work_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("works.id", ondelete="CASCADE"), nullable=False)
    exercise_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("exercises.id", ondelete="SET NULL"))
    general_comment: Mapped[str] = mapped_column(String)

    files: Mapped[list["Files"]] = relationship(
        "Files",
        secondary="answers_files",
        backref="answer",
    )

    exercise: Mapped["Exercises"] = relationship("Exercises", backref="answer")
    work: Mapped["Works"] = relationship("Works", back_populates="answers")
    criterions: Mapped[list["Assessment"]] = relationship(
        "ACriterions",
        backref="answer",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    
    comments: Mapped[list["Comments"]] = relationship(
        "Comments",
        backref="answer",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class Works(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    finish_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    status: Mapped[StatusWork] = mapped_column(Enum(StatusWork), default=StatusWork.draft, nullable=False)
    сonclusion: Mapped[str] = mapped_column(String, nullable=True)

    answers: Mapped[list["Answers"]] = relationship(
        "Answers",
        back_populates="work",
        cascade="all, delete-orphan",
        passive_deletes=True,

    )



