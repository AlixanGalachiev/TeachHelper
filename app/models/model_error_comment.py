import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Enum, DateTime, Integer, ForeignKey, Column, Table
import enum
from .base import Base


class ErrorType(str, enum.Enum):
	Spelling    = "Орфографическая"
	Grammar     = "Грамматическая"
	Punctuation = "Пунктуационная"
	Speech      = "Речевая"
	Stylistic   = "Стилистическая"
	Graphic     = "Графическая"
	Factual     = "Фактическая"
	Logical     = "Логическая"



class ErrorComment(Base):
	type: Mapped[ErrorType] = mapped_column(Enum(ErrorType), nullable=False)
	description: Mapped[str] = mapped_column(String(250), nullable=True) # в будущем добавить автодополнение по типу если с фронта не передали

	work_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
	# work: Mapped["Work"] = relationship("Work", back_populates="error_comments")
















