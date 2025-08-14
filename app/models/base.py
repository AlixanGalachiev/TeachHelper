from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from typing import Any


class Base(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
