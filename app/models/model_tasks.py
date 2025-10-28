from datetime import datetime
import enum
import uuid

from sqlalchemy import UUID, DateTime, Enum, ForeignKey, Integer, String
from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Можно сделать так, чтобы учитель сам заполнял критерии, можно сделать так, чтобы критерии были из ЕГЭ
class ExerciseCriterions(Base):
    __tablename__="exercise_criterions"
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

    criterions: Mapped[list["ExerciseCriterions"]] = relationship(
        "ExerciseCriterions",
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





class Answers(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    submission_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False)
    exercise_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("exercises.id", ondelete="SET NULL"))
    score_recveied: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    file_url: Mapped[str] = mapped_column(String)

    exercise: Mapped["Exercises"] = relationship("Exercises", backref="answer")
    submission: Mapped["Submissions"] = relationship("Submissions", back_populates="answers")


class ErrorTypes(Base):
    __tablename__ = "error_types"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

class Errors(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    answer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("answers.id", ondelete="CASCADE"), nullable=False)
    error_type_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("error_types.id"), nullable=False)
    comment: Mapped[str] = mapped_column(String)

class Subjects(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)



class StatusSubmission(str, enum.Enum):
    draft        = "draft"
    inProgress   = "inProgress"
    verification = "verification"
    verificated  = "verificated"
    canceled     = "canceled"


class Submissions(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    submission_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    total_score: Mapped[int] = mapped_column(Integer, nullable=True)
    status: Mapped[StatusSubmission] = mapped_column(Enum(StatusSubmission), default=StatusSubmission.draft, nullable=False)

    answers: Mapped[list["Answers"]] = relationship(
        "Answers",
        back_populates="submission",
        cascade="all, delete-orphan",
    )
    
