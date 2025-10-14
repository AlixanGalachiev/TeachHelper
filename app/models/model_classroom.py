import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey


from .base import Base

class Classroom(Base):
	name: Mapped[str] = mapped_column(String(50), nullable=False)
	teacher_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)

	# teacher:  Mapped["User"] = relationship(
	# 	"User",
	# 	back_populates="classrooms_teacher"
	# )

	# students: Mapped[list["User"]] = relationship(
	# 	"User",
	# 	secondary=classroom_students,
	# 	back_populates="classroom_student"
	# )

