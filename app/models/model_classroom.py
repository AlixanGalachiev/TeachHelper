from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from .base import Base

class Classrooms(Base):
    name: Mapped[str] = mapped_column(String(50), nullable=False)

