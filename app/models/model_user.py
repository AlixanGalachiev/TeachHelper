import uuid
from sqlalchemy.dialects.postgresql import UUID
from typing import List, Optional
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Enum, DateTime, Integer, ForeignKey
from sqlalchemy import Column, Table
import enum
from datetime import datetime
from typing import Optional

from .base import Base


class Role(str, enum.Enum):
	teacher = "teacher"
	student = "student"


teacher_students = Table(
	"teacher_students",
	Base.metadata,
	Column("teacher_id", UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE")),
	Column("student_id", UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE")),
)


refferal_refferers = Table(
	"refferal_refferers",
	Base.metadata,
	Column("refferal_id", UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True),
	Column("refferer_id", UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True),
)


classroom_students = Table(
    "classroom_students",
    Base.metadata,
    Column("student_id", UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True),
    Column("classroom_id", UUID(as_uuid=True), ForeignKey("classroom.id"), primary_key=True),
)


class User(Base):
	email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
	first_name: Mapped[str] = mapped_column(String(50))
	middle_name: Mapped[str] = mapped_column(String(50))
	last_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
	
	role: Mapped[Role] = mapped_column(Enum(Role), default=Role.student)
	# Пароль хранить в хэше, поле для примера
	password_hash: Mapped[str] = mapped_column(String(255))


	teacher:  Mapped["User"] = relationship("User", secondary=teacher_students, back_populates="students")
	students: Mapped[list["User"]] = relationship("User", secondary=teacher_students, back_populates="teacher")

	classrooms_teacher: Mapped[List["Classroom"]] = relationship("Classroom", back_populates="teacher", cascade="all,delete-orphan")
	classroom_student: Mapped["Classroom"] = relationship("Classroom", secondary=classroom_students, backref="students_in_class")

	refferals: Mapped[list["User"]] = relationship("User", secondary=refferal_refferers, back_populates="refferer")
	refferer: Mapped["User"] = relationship("User", secondary=refferal_refferers, back_populates="refferals")


class TaskType(str, enum.Enum):
	dictation   = "dictation"
	copying     = "copying"
	exposition  = "exposition"
	composition = "composition"

class Task(Base):
	name: Mapped[str] = mapped_column(String(100), index=True)
	type: Mapped[TaskType] = mapped_column(Enum(TaskType), nullable=False, index=True)
	files_url: Mapped[str] = mapped_column(String(250), nullable=True) #ссылка на папку в s3 /tasks/task_uuid/
	description: Mapped[str] = mapped_column(String(150), nullable=True)
	created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
	deadline: Mapped[Any] = mapped_column(DateTime(timezone=True), index=True, nullable=True)


class WorkStatus(str, enum.Enum):
	executing = "executing"
	checking  = "checking"
	archived  = "archived"

class Work(Base):
	status       : Mapped[WorkStatus] = mapped_column(Enum(WorkStatus), nullable=False, index=True, default=WorkStatus.executing)
	files_url    : Mapped[str] = mapped_column(String(100), nullable=False)
	max_point    : Mapped[int] = mapped_column(Integer, nullable=True)
	final_point : Mapped[int] = mapped_column(Integer, nullable=True)
	finish_date  : Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=True)



class Subscription(Base):
	type: Mapped[str] = mapped_column(String(50), nullable=False)
	price: Mapped[int] = mapped_column(Integer, nullable=False)
	description: Mapped[str] = mapped_column(String(250), nullable=False)



class Classroom(Base):
	name: Mapped[str] = mapped_column(String(50), nullable=False)
	teacher_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)

	teacher:  Mapped["User"] = relationship(
     	"User",
		foreign_keys=[teacher_id],
		back_populates="classrooms_teacher"
	)

	students_in_class: Mapped[list["User"]] = relationship(
		"User",
		secondary=classroom_students,
		primaryjoin=id == classroom_students.c.classroom_id,
		secondaryjoin=User.id == classroom_students.c.student_id,
		backref="classrooms"
	)

	



# Настроил связи между 
# учителями - классами, 
# студентами - классами
# рефералы - рефереры
# студенты - учителя


# Еще работы задания учителя учиники