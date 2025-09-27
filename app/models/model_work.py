import uuid
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from typing import List, Optional
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Enum, DateTime, Integer, ForeignKey, Column, Table, Boolean

import enum
from datetime import datetime
from typing import Optional
from datetime import datetime

from .base import Base


class WorkStatus(str, enum.Enum):
	draft       = "черновик"
	in_work     = "выполняется"
	on_checking = "проверяется"
	checked     = "проверена"
	archived    = "в архиве"


class Work(Base):
	status       : Mapped[WorkStatus] = mapped_column(Enum(WorkStatus), index=True, default=WorkStatus.draft, nullable=False)
	images        : Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
	points       : Mapped[int] = mapped_column(Integer, nullable=True)
	finish_date  : Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
	teacher_comment: Mapped[str] = mapped_column(String(250), nullable=True)
	verifed_by_ai: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

	task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("task.id"), nullable=False)
	student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

	task: Mapped["Task"] = relationship("Task", back_populates="works")
	student: Mapped[list["User"]] = relationship("User", back_populates="works")

	error_comments: Mapped[list["ErrorComment"]] = relationship("ErrorComment", back_populates="work", cascade="all, delete-orphan")
	
