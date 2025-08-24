from typing import Sequence, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.hash import bcrypt

from app.models.models import *
from app.schemas.schema_user import UserCreate
from app.utils.password import get_password_hash
from datetime import datetime


class WorkRepo:
	def __init__(self, session: AsyncSession):
		self.session = session
	
	@staticmethod
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


	@staticmethod
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


	@staticmethod
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


	@staticmethod
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


class TaskRepo:

	@staticmethod
	async def detail(
		self: AsyncSession,
		task_id: uuid.UUID
	):
		task = await self.session.get(Task, task_id)
		if not task:
			raise HTTPException(404, message="This work doesn't exists")

		return task


	@staticmethod
	async def get_all(
		self: AsyncSession,
		teacher_id: uuid.UUID,
		offset: int = 0,
		limit: int = 10
	)
		stmt = (
			select(Task)
			.where(Task.teacher_id == teacher_id)
			.group_by(Task.updated_at)
			.offset(offset)
			.limit(limit)
		)
		result = await self.session.execute(stmt)
		rows = result.scalars.all()
		return rows

	
	@staticmethod
	async def update(
		self,
		task_id: uuid.UUID,
		updates: TaskUpdate
	):
		task = await self.session.get(Task, task_id)
		if not task:
			raise HTTPException(404, message="This task doesn't exist")

		# обновляем только те поля, которые переданы
		for field, value in updates.dict(exclude_unset=True).items():
			setattr(task, field, value)

		await self.session.flush()  # сохраняем изменения
		return task


	@staticmethod
	async def delete(self, task_id: uuid.UUID):
		task = await self.session.get(Task, task_id)
		if not task:
			raise HTTPException(404, message="This task doesn't exist")

		await self.session.delete(task)
		await self.session.flush()
		return task



class ClassroomRepo:
    def __init__(self, session: AsyncSession):
        self.session = session


	@staticmethod
	async def get_statistic(self, classroom_id: UUID):
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


	@staticmethod
	async def add_student(self, classroom_id: UUID, student_id: UUID):
        # Проверяем, что студент ещё не в классе
        stmt = select(classroom_students).where(
            classroom_students.c.classroom_id == classroom_id,
            classroom_students.c.student_id == student_id
        )
        exists = await self.session.execute(stmt)
        if exists.first():
            raise HTTPException(400, detail="Student already in classroom")

        await self.session.execute(
            classroom_students.insert().values(classroom_id=classroom_id, student_id=student_id)
        )
        await self.session.flush()
        return {"message": "Student added"}


	@staticmethod
	async def remove_student(self, classroom_id: UUID, student_id: UUID):
        stmt = delete(classroom_students).where(
            classroom_students.c.classroom_id == classroom_id,
            classroom_students.c.student_id == student_id
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return {"deleted": result.rowcount}


	@staticmethod
	async def rename(self, classroom_id: UUID, new_name: str):
        stmt = (
            update(Classroom)
            .where(Classroom.id == classroom_id)
            .values(name=new_name)
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(stmt)
        await self.session.flush()
        return {"message": f"Classroom renamed to {new_name}"}


	@staticmethod
	async def delete(self, classroom_id: UUID):
        # Сначала удаляем связи с учениками
        await self.session.execute(
            delete(classroom_students).where(classroom_students.c.classroom_id == classroom_id)
        )
        # Потом сам класс
        stmt = delete(Classroom).where(Classroom.id == classroom_id)
        await self.session.execute(stmt)
        await self.session.flush()
        return {"message": "Classroom deleted"}


class SubscriptionCreate(BaseModel):
	type: SubscriptionType
	price: int
	description: str
 
class SubscriptionRead(SubscriptionCreate):
	id: uuid.UUID

class SubscriptionUpdate(BaseModel):
    id:          uuid.UUID
	price:       int               | None = None
	description: str               | None = None
	type:        SubscriptionType  | None = None

class SubscriptionRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: SubscriptionCreate) -> SubscriptionRead:
        new_sub = Subscription(
            id=uuid.uuid4(),
            type=data.type,
            price=data.price,
            description=data.description
        )
        self.session.add(new_sub)
        await self.session.commit()
        await self.session.refresh(new_sub)
        return SubscriptionRead.model_validate(new_sub)

    async def get(self, id: uuid.UUID) -> SubscriptionRead | None:
        query = select(Subscription).where(Subscription.id == id)
        result = await self.session.execute(query)
        sub = result.scalar_one_or_none()
        if not sub:
            raise HTTPException(404, detail="This subscription doesn't exists")

        return SubscriptionRead.model_validate(sub)

    async def update(self, data: SubscriptionUpdate) -> SubscriptionRead | None:
        query = (
            update(Subscription)
            .where(Subscription.id == data.id)
            .values(
                price=data.price if data.price is not None else Subscription.price,
                description=data.description if data.description is not None else Subscription.description,
                type=data.type if data.type is not None else Subscription.type,
            )
            .returning(Subscription)
        )
        result = await self.session.execute(query)
        updated = result.scalar_one_or_none()
        if not updated:
            raise HTTPException(404, detail="This subscription doesn't exists")

        await self.session.commit()
        return SubscriptionRead.model_validate(updated)

    async def delete(self, id: uuid.UUID) -> bool:
        query = delete(Subscription).where(Subscription.id == id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0




class UserRepo:
	def __init__(self, session: AsyncSession):
		self.session = session

	async def create(self, user_data: UserCreate) -> User:
		user = User(
			email=user_data.email,
			password_hash=get_password_hash(user_data.password),
			full_name=user_data.full_name,
			role=user_data.role,
		)
		self.session.add(user)
		await self.session.flush()
		return user

	async def get(self, user_id: int) -> Optional[User]:
		res = await self.session.execute(select(User).where(User.id == user_id))
		return res.scalar_one_or_none()

	async def get_by_email(self, email: str) -> Optional[User]:
		res = await self.session.execute(select(User).where(User.email == email))
		return res.scalar_one_or_none()

	async def list(self, limit: int = 100, offset: int = 0) -> Sequence[User]:
		res = await self.session.execute(select(User).offset(offset).limit(limit))
		return res.scalars().all()

	async def update(self, user_id: int, **fields) -> Optional[User]:
		if "password" in fields:
			fields["password_hash"] = bcrypt.hash(fields.pop("password"))
		await self.session.execute(update(User).where(User.id == user_id).values(**fields))
		await self.session.flush()
		return await self.get(user_id)

	async def delete(self, user_id: int) -> bool:
		await self.session.execute(delete(User).where(User.id == user_id))
		return True


