import uuid
from sqlalchemy.dialects.postgresql import UUID
from typing import List, Optional
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Enum, DateTime, Integer, ForeignKey, Column, Table
from sqlalchemy.ext.asyncio import AsyncAttrs

import enum
from datetime import datetime
from typing import Optional
from datetime import datetime

from .base import Base



class TaskType(str, enum.Enum):
	dictation   = "dictation"
	copying     = "copying"
	exposition  = "exposition"
	composition = "composition"



from pydantic import BaseModel

class CreateTask(BaseModel):
	name:        str
	type:        TaskType
	max_point:   int
	teacher_id:  uuid.UUID

	files_url:   str      | None = None
	description: str      | None = None
	deadline:    datetime | None = None

class Task(Base):
	name: Mapped[str] = mapped_column(String(100), index=True)
	type: Mapped[TaskType] = mapped_column(Enum(TaskType), nullable=False, index=True)
	files_url: Mapped[str] = mapped_column(String(250), nullable=True) #ссылка на папку в s3 /tasks/task_uuid/
	max_point: Mapped[int] = mapped_column(Integer, nullable=False)
	description: Mapped[str] = mapped_column(String(150), nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
	deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
 

	teacher_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
	teacher: Mapped["User"] = relationship("User", back_populates="tasks")
	works: Mapped[list["Work"]] = relationship("Work", back_populates="task")



