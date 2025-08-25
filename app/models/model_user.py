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
from datetime import datetime

from .base import Base



classroom_students = Table(
	"classroom_students",
	Base.metadata,
	Column("student_id", UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True),
	Column("classroom_id", UUID(as_uuid=True), ForeignKey("classroom.id"), primary_key=True),
)


teacher_students = Table(
	"teacher_students",
	Base.metadata,
	Column("teacher_id", UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True),
	Column("student_id", UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True),
)

refferal_refferers = Table(
	"refferal_refferers",
	Base.metadata,
	Column("refferal_id", UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True),
	Column("refferer_id", UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True),
)



class RoleUser(str, enum.Enum):
	teacher = "teacher"
	student = "student"


class User(Base):
	email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
	first_name: Mapped[str] = mapped_column(String(50))
	middle_name: Mapped[str] = mapped_column(String(50))
	last_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
	
	role: Mapped[RoleUser] = mapped_column(Enum(RoleUser), default=RoleUser.student)
	# Пароль хранить в хэше, поле для примера
	password_hash: Mapped[str] = mapped_column(String(255))
	subscription_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("subscription.id"), nullable=True)


	teacher:  Mapped["User"] = relationship(
		"User",
		secondary=teacher_students,
		primaryjoin=lambda: User.id == teacher_students.c.student_id,
		secondaryjoin=lambda: User.id == teacher_students.c.teacher_id,
		back_populates="students"
	)

	students: Mapped[list["User"]] = relationship(
		"User",
		secondary=teacher_students,
		primaryjoin=lambda: User.id == teacher_students.c.teacher_id,
		secondaryjoin=lambda: User.id == teacher_students.c.student_id,
		back_populates="teacher"
  	)

	classrooms_teacher: Mapped[List["Classroom"]] = relationship("Classroom", back_populates="teacher", cascade="all,delete-orphan")
	classroom_student: Mapped["Classroom"] = relationship("Classroom", secondary=classroom_students, back_populates="students")

	refferals: Mapped[list["User"]] = relationship(
		"User",
		secondary=refferal_refferers,
		primaryjoin=lambda: User.id == refferal_refferers.c.refferer_id,
		secondaryjoin=lambda: User.id == refferal_refferers.c.refferal_id,
		back_populates="refferer"
	)
	refferer: Mapped["User"] = relationship(
		"User",
		secondary=refferal_refferers,
		primaryjoin=lambda: User.id == refferal_refferers.c.refferal_id,
		secondaryjoin=lambda: User.id == refferal_refferers.c.refferer_id,
		back_populates="refferals"
	)

	tasks: Mapped[list["Task"]] = relationship("Task", back_populates="teacher")
	work:  Mapped["Work"] = relationship("Work", back_populates="students")

	subscription: Mapped["Subscription"] = relationship("Subscription", back_populates="users")
