from datetime import datetime
import enum
import uuid

from sqlalchemy import UUID, Column, ForeignKey, Integer, String, Table
from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Comments(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    answer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("answers.id", ondelete="CASCADE"), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False, default="")
    type_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("comment_types.id"), nullable=False)

    files: Mapped[list["Files"]] = relationship(
        "Files",
        secondary="comments_files",
        backref="comment",
        cascade="all, delete-orphan",
        single_parent=True
    )


class CommentTypes(Base):
    __tablename__="comment_types"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    short_name: Mapped[str] = mapped_column(String(10), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
