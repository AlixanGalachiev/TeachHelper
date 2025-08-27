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


	async def create(self, name: str, teacher_id: int) -> Classroom:
		classroom = Classroom(name=name, teacher_id=teacher_id)
		self.session.add(classroom)
		await self.session.flush()
		return classroom


	async def get(self, classroom_id: int) -> Optional[Classroom]:
		res = await self.session.execute(
			select(Classroom)
			.where(Classroom.id == classroom_id)
			.options(selectinload(Classroom.students))
			)
		return res.scalar_one_or_none()


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


	# async def add_student(self, classroom_id: uuid.UUID, student_id: uuid.UUID):
	#     # Проверяем, что студент ещё не в классе
	#     stmt = select(classroom_students).where(
	#         classroom_students.c.classroom_id == classroom_id,
	#         classroom_students.c.student_id == student_id
	#     )
	#     exists = await self.session.execute(stmt)
	#     if exists.first():
	#         raise HTTPException(400, detail="Student already in classroom")

	#     await self.session.execute(
	#         classroom_students.insert().values(classroom_id=classroom_id, student_id=student_id)
	#     )
	#     await self.session.flush()
	#     return {"message": "Student added"}


	# async def remove_student(self, classroom_id: uuid.UUID, student_id: uuid.UUID):
	#     stmt = delete(classroom_students).where(
	#         classroom_students.c.classroom_id == classroom_id,
	#         classroom_students.c.student_id == student_id
	#     )
	#     result = await self.session.execute(stmt)
	#     await self.session.flush()
	#     return {"deleted": result.rowcount}



	# async def delete(self, classroom_id: uuid.UUID):
	#     # Сначала удаляем связи с учениками
	#     await self.session.execute(
	#         delete(classroom_students).where(classroom_students.c.classroom_id == classroom_id)
	#     )
	#     # Потом сам класс
	#     stmt = delete(Classroom).where(Classroom.id == classroom_id)
	#     await self.session.execute(stmt)
	#     await self.session.flush()
	#     return {"message": "Classroom deleted"}


