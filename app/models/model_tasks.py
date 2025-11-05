from datetime import datetime
import enum
import uuid

from fastapi import HTTPException, logger
from sqlalchemy import UUID, Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Table
from app.config.boto import get_boto_client
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
    
    works: Mapped[list["Works"]] = relationship(
        "Works",
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

class ACriterions(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    answer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("answers.id", ondelete="CASCADE"), nullable=False)
    e_criterion_id:  Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("e_criterions.id", ondelete="CASCADE"), nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

class Answers(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    work_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("works.id", ondelete="CASCADE"), nullable=False)
    exercise_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("exercises.id", ondelete="SET NULL"))

    files: Mapped[list["Files"]] = relationship(
        "Files",
        secondary="answers_files",
        backref="answer",
        cascade="all, delete-orphan",
        passive_deletes=True        
    )

    exercise: Mapped["Exercises"] = relationship("Exercises", backref="answer")
    work: Mapped["Works"] = relationship("Works", back_populates="answers")
    criterions: Mapped[list["ACriterions"]] = relationship(
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

    answers: Mapped[list["Answers"]] = relationship(
        "Answers",
        back_populates="work",
        cascade="all, delete-orphan",
        passive_deletes=True,

    )

class Subjects(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)


comments_files = Table(
    "comments_files",
    Base.metadata,
    Column("id", UUID(as_uuid=True)),
    Column("file_id", ForeignKey("files.id", ondelete="CASCADE"), nullable=False),
    Column("comment_id", ForeignKey("comments.id"), nullable=False)
)

answers_files = Table(
    "answers_files",
    Base.metadata,
    Column("id", UUID(as_uuid=True)),
    Column("file_id", ForeignKey("files.id", ondelete="CASCADE"), nullable=False),
    Column("answer_id", ForeignKey("answers.id"), nullable=False)
)


class TypeComment(enum.Enum):
    1 = "Речевая"
    2 = "Этическая"
    3 = "Пунктуационная"
    4 = "Грамматическая"
    5 = "Логическая"
    6 = "Стилистическая"
    7 = "Орфографическая"
    8 = "Комментарий к фрагменту"

class Comments(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    answer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("answers.id", ondelete="CASCADE"), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False, default="")
    type_id: Mapped[int] = mapped_column(Integer, ForeignKey("type_comments.id"), nullable=False)

    files: Mapped[list["Files"]] = relationship(
        "Files",
        secondary="comments_files",
        backref="comment"
    )

from sqlalchemy import event

class TypeComments(Base):
    __tablename__="type_comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, default=uuid.uuid4)
    short_name: Mapped[str] = mapped_column(String(10), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)


class Files(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    bucket: Mapped[str] = mapped_column(String, nullable=False)
    original_size: Mapped[int] = mapped_column(Integer, nullable=False)
    original_mime: Mapped[int] = mapped_column(Integer, nullable=False)


@event.listens_for(Files, 'before_delete')
async def delete_file_from_minio(mapper, connection, target):
    s3 = await get_boto_client()
    try:
        await s3.delete_object(Bucket=target.bucket, Key=f"{target.id}/{target.filename}")
    except Exception as exc:
        logger.exception(exc)
        raise HTTPException(status_code=500, detail="Internal Server Error")