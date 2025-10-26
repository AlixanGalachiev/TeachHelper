import uuid
from sqlalchemy import func, insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.model_tasks import Submissions, Tasks


from app.models.model_users import RoleUser, Users, teachers_students

class RepoStudents:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, teacher):
        stmt = (
            select(
                Users.id,
                func.concat(Users.first_name, " ", Users.last_name).label("name"),
                teachers_students.c.classroom_id
            ).select_from(Users)
            .where(Users.role == RoleUser.student)
            .join(teachers_students, Users.id == teachers_students.c.student_id)
            .where(teachers_students.c.teacher_id == teacher.id)
        )
        
        result = await self.session.execute(stmt)
        return result.mappings().all()


    async def get_performans_data(self, student_id: uuid.UUID):
        agg_stmt = (
            select(
                Users.id.label("student_id"),
                func.concat(Users.first_name, " ", Users.last_name).label("student_name"),
                func.count().filter(Submissions.status == "verificated").label("verificated_works_count"),
                func.avg(Submissions.total_score).filter(Submissions.status == "verificated").label("avg_score"),
            )
            .where(Users.id == student_id)
            .outerjoin(Submissions, Users.id == Submissions.student_id)
            .group_by(Users.id, Users.first_name, Users.last_name)
        )
        agg_result = await self.session.execute(agg_stmt)
        agg_data = agg_result.mappings().first()

        works_stmt = (
            select(
                Submissions.id.label("submission_id"),
                Submissions.student_id.label('student_id'),
                Submissions.status,
                Submissions.total_score,
                Tasks.title.label("task_title"),
                Tasks.max_score
            )
            .join(Tasks, Submissions.task_id == Tasks.id)
            .where(Submissions.student_id == student_id)
        )
        works_result = await self.session.execute(works_stmt)
        works_data = works_result.mappings().all()

        return {
            **agg_data,
            "works": works_data
        }



    async def user_exists_in_class(self, teacher_id: uuid.UUID, student_id: uuid.UUID, classroom_id: uuid.UUID):
        stmt = (
            select(func.count())
            .select_from(teachers_students)
            .where(teachers_students.c.teacher_id == teacher_id)
            .where(teachers_students.c.student_id == student_id)
            .where(teachers_students.c.classroom_id == classroom_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar() > 0


    async def exists(self, teacher_id: uuid.UUID, student_id: uuid.UUID):
        stmt = (
            select(func.count())
            .select_from(teachers_students)
            .where(teachers_students.c.teacher_id == teacher_id)
            .where(teachers_students.c.student_id == student_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar() > 0


    async def move_to_class(self, teacher_id: uuid.UUID, student_id: uuid.UUID, classroom_id: uuid.UUID):
        stmt = (
            update(teachers_students)
            .where(teachers_students.c.teacher_id == teacher_id)
            .where(teachers_students.c.student_id == student_id)
            .values(classroom_id = classroom_id)
        )
        await self.session.execute(stmt)

    async def remove_from_class(self, teacher_id: uuid.UUID, student_id: uuid.UUID):
        stmt = (
            update(teachers_students)
            .where(teachers_students.c.teacher_id == teacher_id)
            .where(teachers_students.c.student_id == student_id)
            .values(classroom_id = None)
        )
        await self.session.execute(stmt)


    async def delete(self, teacher_id: uuid.UUID, student_id: uuid.UUID):
        stmt = (
            delete(teachers_students)
            .where(teachers_students.c.teacher_id == teacher_id)
            .where(teachers_students.c.student_id == student_id)
        )
        await self.session.execute(stmt)

    async def add_teacher(self, teacher_id: uuid.UUID, student_id: uuid.UUID):
        stmt = (
            insert(teachers_students)
            .values(teacher_id=teacher_id, student_id=student_id)
        )
        await self.session.execute(stmt)
        