import uuid

from sqlalchemy import UUID, Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

subjects_comments_types = Table(
    "subjects_comment_types",
    Base.metadata,
    Column[uuid.UUID]("id", UUID(as_uuid=True)),
    Column[uuid.UUID]("comment_type_id", ForeignKey("comment_types.id", ondelete="CASCADE"), nullable=False),
    Column[uuid.UUID]("subject_id", ForeignKey("subjects.id"), nullable=False)
)

class Subjects(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)

    comment_types: Mapped[list["CommentTypes"]] = relationship(
        "CommentTypes",
        secondary="subjects_comment_types",
    )