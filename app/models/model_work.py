import uuid
from sqlalchemy.dialects.postgresql import UUID
from typing import List, Optional
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Enum, DateTime, Integer, ForeignKey, Column, Table
import enum
from datetime import datetime
from typing import Optional
from datetime import datetime

from .base import Base



class WorkStatus(str, enum.Enum):
	draft     = "draft"
	executing = "executing"
	checking  = "checking"
	archived  = "archived"



from pydantic import BaseModel

class CreateWork(BaseModel):
	files_url:  str
	task_id:    uuid.UUID
	student_id: uuid.UUID

	status: WorkStatus    | None = None
	points:      int      | None = None
	finish_date: datetime | None = None


class Work(Base):
	status       : Mapped[WorkStatus] = mapped_column(Enum(WorkStatus), index=True, default=WorkStatus.draft, nullable=False)
	files_url    : Mapped[str] = mapped_column(String(100), nullable=False)
	points       : Mapped[int] = mapped_column(Integer, nullable=True)
	finish_date  : Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=True)

	task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("task.id"), nullable=False)
	student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

	task: Mapped["Task"] = relationship("Task", back_populates="works")
	student: Mapped[list["User"]] = relationship("User", back_populates="works")
	
