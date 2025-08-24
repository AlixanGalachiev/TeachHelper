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
from .model_user import classroom_students

class Classroom(Base):
	name: Mapped[str] = mapped_column(String(50), nullable=False)
	teacher_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)

	teacher:  Mapped["User"] = relationship(
		"User",
		foreign_keys=[teacher_id],
		back_populates="classrooms_teacher"
	)

	students: Mapped[list["User"]] = relationship(
		"User",
		secondary=classroom_students,
		backref="classrooms"
	)

