import uuid
from app.models import User, WorkStatus, Task, Work, Classroom
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects import postgresql


class WorkRepo:
	def __init__(self, session: AsyncSession):
		self.session = session

	# async def teacher_get_works(
	# 	self,
	# 	teacher_id : uuid.UUID,
	# 	statuses     : list[WorkStatus],
	# 	limit      : int,
	# 	offset     : int,
	# 	students_ids : list[uuid.UUID] | None  = None,
	# ):
	# 	Teacher = aliased(User)
	# 	Student = aliased(User)

	# 	stmt = (
	# 		select(
	# 			Work.id.label('work_id'),
	# 			Student.first_name,
	# 			Student.middle_name,
	# 			Student.last_name,
	# 			Task.max_point,
	# 			Work.points,
	# 			Work.status,
	# 			Task.name.label("task_name"),
	# 		)
	# 		.join(Task, Task.id == Work.task_id)
	# 		.join(Student, Student.id == Work.student_id)
	# 		.join(Teacher, Teacher.id == Task.teacher_id)
	# 	)

	# 	filters = [
    #   		Teacher.id == teacher_id,
	# 		Work.status != WorkStatus.draft
    #     ]

	# 	if student_id is not None and class_name is None:
	# 		filters.extend([
	# 			Work.student_id == student_id
	# 		])

	# 	elif class_name is not None and student_id is None:
	# 		stmt = stmt.join(Classroom, Classroom.teacher_id == Teacher.id)
	# 		stmt = stmt.join(classroom_students, classroom_students.c.classroom_id == Classroom.id)
	# 		filters.extend([
	# 			Classroom.name == class_name,
	# 			Student.id == classroom_students.c.student_id
	# 		])

	# 	if statuses is not None:
	# 		filters.append(Work.statusst._in(statuses))

	# 	stmt = stmt.where(*filters).limit(limit).offset(offset)

	# 	result = await self.session.execute(stmt)
	# 	rows = result.mappings().all()
	# 	return rows



	async def student_get_works(
		self,
		student_id: uuid.UUID,
		limit: int,
		offset: int,
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
				Work.id.label("work_id"),
				Task.name.label("taskname"),
				Task.description.label("description"),
				Student.first_name.label("first_name"),
				Student.middle_name.label("middle_name"),
				Student.last_name.label("last_name"),
				Work.points.label("points"),
				Task.max_point.label("max_point"),
				Work.files.label("work_files"),
				Task.files.label("task_files")
				# comment
			)
			.join(Task, Task.id == Work.task_id)
			.join(Student, Student.id == Work.student_id)
			.where(
				Work.id == work_id
			)
		)

		result = await self.session.execute(stmt)
		row = result.mappings().one_or_none()
		return row
