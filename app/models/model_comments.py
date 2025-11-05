from datetime import datetime
import enum
import uuid

from sqlalchemy import UUID, Column, ForeignKey, Integer, String, Table
from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

comments_files = Table(
    "comments_files",
    Base.metadata,
    Column("id", UUID(as_uuid=True)),
    Column("file_id", ForeignKey("files.id", ondelete="CASCADE"), nullable=False),
    Column("comment_id", ForeignKey("comments.id"), nullable=False)
)


class Comments(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    answer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("answers.id", ondelete="CASCADE"), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False, default="")
    type_id: Mapped[int] = mapped_column(Integer, ForeignKey("type_comments.id"), nullable=False)

    files: Mapped[list["Files"]] = relationship(
        "Files",
        secondary="comments_files",
        backref="comment"
    )


class TypeComments(Base):
    __tablename__="type_comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, default=uuid.uuid4)
    short_name: Mapped[str] = mapped_column(String(10), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
