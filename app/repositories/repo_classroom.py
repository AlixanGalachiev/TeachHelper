import uuid
from typing import Optional, Sequence
from sqlalchemy import select, delete, insert, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.model_classroom import Classroom
from app.models.model_user import User, classroom_students
from app.models.model_work import Work
from app.models.model_task import Task


class ClassroomRepo:
	def __init__(self, session: AsyncSession):
		self.session = session

	async def get_statistic(self, classroom_id: uuid.UUID):
		# Получаем студентов в классе
		stmt = (
			select(
				User.id,
				User.first_name,
				User.last_name,
				Work.id,
				Work.status,
				Task.name.label('taskname'),
				Task.max_points,
				Work.points,
				Work.updated_at
			)
			.join(classroom_students, classroom_students.c.student_id == User.id)
			.join(Work, User.id == Work.student_id)
			.join(Task, Task.id == Work.task_id)
			.where(
				classroom_students.c.classroom_id == classroom_id,
			)
		)

		result = await self.session.execute(stmt)
		students = result.all()

		return {
			"classroom_id": classroom_id,
			"student_count": len(students),
			"students": [{"id": s.id, "first_name": s.first_name, "last_name": s.last_name} for s in students]
		}
