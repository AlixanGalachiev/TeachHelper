import uuid
from app.models import User, WorkStatus, Task, Work, Classroom, classroom_students
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pprint import pprint
from sqlalchemy.dialects import postgresql


class WorkRepo:
	def __init__(self, session: AsyncSession):
		self.session = session

	async def teacher_get_works(
		self,
		teacher_id : uuid.UUID,
		class_name : str | None        = None,
		student_id : uuid.UUID | None  = None,
		status     : WorkStatus | None = None,
		limit      : int = 10,
		offset     : int = 0,
	):
		Teacher = aliased(User)
		Student = aliased(User)

		stmt = (
			select(
				Work.id.label('work_id'),
				Student.first_name,
				Student.middle_name,
				Student.last_name,
				Task.max_point,
				Work.points,
				Work.status,
				Task.name.label("task_name"),
			)
			.join(Task, Task.id == Work.task_id)
			.join(Student, Student.id == Work.student_id)
			.join(Teacher, Teacher.id == Task.teacher_id)
		)

		filters = [
      		Teacher.id == teacher_id,
			Work.status != WorkStatus.draft
        ]

		if student_id is not None and class_name is None:
			filters.extend([
				Work.student_id == student_id
			])

		elif class_name is not None and student_id is None:
			stmt = stmt.join(Classroom, Classroom.teacher_id == Teacher.id)
			stmt = stmt.join(classroom_students, classroom_students.c.classroom_id == Classroom.id)
			filters.extend([
				Classroom.name == class_name,
				Student.id == classroom_students.c.student_id
			])

		if status is not None:
			filters.append(Work.status == status)

		stmt = stmt.where(*filters).limit(limit).offset(offset)

		result = await self.session.execute(stmt)
		rows = result.mappings().all()
		return rows



	async def student_get_works(
		self,
		student_id: uuid.UUID,
		limit: int = 10,
		offset: int = 0,
	):
		Teacher = aliased(User)
		Student = aliased(User)

		stmt = (
			select(
				Task.name.label("taskname"),
				Student.first_name,
				Student.middle_name,
				Student.last_name,
				Work.status,
				Task.max_point.label('max_points'),
				Work.points,
				Work.created_at,
			)
			.join(Task, Task.id == Work.task_id)
			.join(Student, Student.id == Work.student_id)
			.where(
				Student.id == student_id
			)
			.order_by(Work.updated_at)
			.limit(limit)
			.offset(offset)
		)

		result = await self.session.execute(stmt)
		rows = result.mappings().all()
		return rows

	async def detail(
		self,
		work_id: uuid.UUID,
	):
		Student = aliased(User)

		stmt = (
			select(
				Task.name.label("taskname"),
				Student.first_name,
				Student.middle_name,
				Student.last_name,
				Work.points,
				Task.max_point,
				Work.files_url.label("work_files_url"),
				Task.files_url.label("task_files_url"),
				# comment
			)
			.join(Task, Task.id == Work.task_id)
			.join(Student, Student.id == Work.student_id)
			.where(
				Work.id == work_id
			)
		)

		result = await self.session.execute(stmt)
		rows = result.all()
		return rows

