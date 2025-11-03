from datetime import datetime
import enum
import uuid

from sqlalchemy import UUID, Boolean, DateTime, Enum, ForeignKey, Integer, String
from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Можно сделать так, чтобы учитель сам заполнял критерии, можно сделать так, чтобы критерии были из ЕГЭ
class ECriterions(Base):
    __tablename__="e_criterions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)

    exercise_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(), nullable=False)
    score: Mapped[int] = mapped_column(Integer(), nullable=False)


class Exercises(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(), nullable=False)
    description: Mapped[str] = mapped_column(String())
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)

    criterions: Mapped[list["ECriterions"]] = relationship(
        "ECriterions",
        backref="exercise",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

class Tasks(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    teacher_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(), nullable=False)
    description: Mapped[str] = mapped_column(String())
    deadline: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    teacher: Mapped["Users"] = relationship(
        "Users",
        backref="tasks")

    exercises: Mapped[list["Exercises"]] = relationship(
        "Exercises",
        backref="task",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )



class StatusWork(str, enum.Enum):
    draft        = "draft"
    inProgress   = "inProgress"
    verification = "verification"
    verificated  = "verificated"
    canceled     = "canceled"

class ErrorTypes(Base): 
    __tablename__ = "error_types"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("works.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

class Errors(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    answer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("answers.id", ondelete="CASCADE"), nullable=False)
    error_type_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("error_types.id"), nullable=False)
    comment: Mapped[str] = mapped_column(String)

class ACriterions(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    answer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("answers.id", ondelete="CASCADE"), nullable=False)
    e_criterion_id:  Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("e_criterions.id", ondelete="CASCADE"), nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

class Answers(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    work_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("works.id", ondelete="CASCADE"), nullable=False)
    exercise_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("exercises.id", ondelete="SET NULL"))
    file_url: Mapped[str] = mapped_column(String, nullable=True)

    exercise: Mapped["Exercises"] = relationship("Exercises", backref="answer")
    work: Mapped["Works"] = relationship("Works", back_populates="answers")
    criterions: Mapped[list["ACriterions"]] = relationship(
        "ACriterions",
        backref="answer",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

class Works(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=False)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    finish_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    status: Mapped[StatusWork] = mapped_column(Enum(StatusWork), default=StatusWork.draft, nullable=False)

    answers: Mapped[list["Answers"]] = relationship(
        "Answers",
        back_populates="work",
        cascade="all, delete-orphan",
        passive_deletes=True,

    )

class Subjects(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)



