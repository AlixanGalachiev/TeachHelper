import uuid
from app.models import User, WorkStatus, Task

class WorkRepo:
	def __init__(self, session: AsyncSession):
		self.session = session
	
	async def teacher_get_worksAI(
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
				Student.first_name,
				Student.middle_name,
				Student.last_name,
				Work.max_point,
				Work.final_point,
				Work.status,
				Task.name.label("task_name"),
			)
			.join(Task, Task.id == Work.task_id)
			.join(Teacher, Teacher.id == Task.teacher_id)
			.join(Student, Student.id == Work.student_id)
			.join(Classroom, Classroom.teacher_id == Teacher.id)
		)

		filters = [Teacher.id == teacher_id]

		if student_id is not None and class_name is None:
			filters.extend([
				Work.student_id == student_id
			])

		elif class_name is not None and student_id is None:
			filters.extend([
				Classroom.name == class_name
			])

		if status is not None:
			filters.append(Work.status == status)

		stmt = stmt.where(*filters).limit(limit).offset(offset)

		result = await self.session.execute(stmt)
		rows = result.all()
		return rows


	async def teacher_get_works(
		self,
		teacher_id: uuid.UUID,
		student_id: uuid.UUID | None = None,
		class_name: str | None = None,
		status: WorkStatus | None = None,
		limit: int = 10,
		offset: int = 0,
	):
	
		stmt = (
			select(
				User.first_name,
				User.middle_name,
				User.last_name,
				Work.max_point,
				Work.final_point,
				Work.status,
				Task.name.label('task_name'),
			)
			.join(Task, User.id == Task.teacher_id)
			.join(Work, Work.task_id == Task.id)
			.join(User, User.id == Work.student_id)
		)

		if student_id is not None and class_name is None:
			stmt = stmt.where(
				Task.teacher_id == teacher_id,
				Work.student_id == student_id,
				Work.status == status
			)

		elif class_name is not None and student_id is None:
			student_ids = await self.session.execute(
				select(teacher_students.c.student_id)
				.join(Classroom, teacher_id == Classroom.teacher_id)
				.where(
					teacher_students.c.teacher_id == teacher_id,
					Classroom.name == class_name
				)
			).scalars().all()

			stmt = stmt.where(
				Task.teacher_id == teacher_id,
				Work.student_id.in_(student_ids),
				Work.status == status
			)
		stmt = stmt.limit(limit).offset(offset)

		result = await self.session.execute(stmt)
		rows = result.all()
		return rows


	async def create_work(
		self,
		files_url   : str,
		task_id     : uuid.UUID,
		student_id  : uuid.UUID,
		finish_date : datetime | None = None,
	):
		work = Work(
			status      = WorkStatus.draft,
			files_url   = files_url,
			max_point   = max_point,
			finish_date = finish_date,
			task_id     = task_id,
			student_id  = student_id,
		)

		self.session.add(work)
		await self.session.flush()
		return work


	async def update_work(self, work_id: int, files_url: str):	
		work = await self.session.get(Work, work_id)
		if not work:
			raise HTTPException(404, message="This work doesn't exists")

		if work.status not in [WorkStatus.draft, WorkStatus.executing]:
			raise HTTPException(403, message="This work is already sended")

		work.files_url = files_url
		await self.session.flush()
		return work

	

	async def student_get_works(
		self,
		student_id: uuid.UUID,
		limit: int = 10,
		offset: int = 0,
	)
		Teacher = aliased(User)
		Student = aliased(User)

		stmt = (
			select(
				Task.name.label("taskname"),
				Student.name.label("username"),
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
			.limit(limit)
			.offset(offset)
		)

		result = await self.session.execute(stmt)
		rows = result.all()
		return rows

	async def detail(
		self,
		work_id: uuid.UUID,
	):
		Student = aliased(User)

		stmt = (
			select(
				Task.name.label("taskname"),
				Student.name.label("username"),
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
			.limit(limit)
			.offset(offset)
		)

		result = await self.session.execute(stmt)
		rows = result.all()
		return rows

