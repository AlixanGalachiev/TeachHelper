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


class SubscriptionType(enum.Enum):
    free    = "free"
    mininal = "mininal"
    medium  = "medium"
    max     = "max"

class Subscription(Base):
	type: Mapped[SubscriptionType] = mapped_column(Enum(SubscriptionType), nullable=False, index=True)
	price: Mapped[int] = mapped_column(Integer, nullable=False)
	description: Mapped[str] = mapped_column(String(250), nullable=False)

	# users: Mapped[list["User"]] = relationship("User", back_populates="subscription")


