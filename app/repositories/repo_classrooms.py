

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload, load_only

from app.models.model_classroom import Classrooms
from app.models.model_users import Users, users_classrooms, teachers_students


class RepoClassroom():
    def __init__(self, session):
        self.session = session

    async def exists(self, name: str|None = None, classroom_id: uuid.UUID|None = None, user_id: uuid.UUID|None = None):
        stmt = select(func.count()).select_from(Classrooms)
        
        if user_id is not None:
            stmt = stmt.join(users_classrooms, Classrooms.id == users_classrooms.c.classroom_id)
            stmt = stmt.where(users_classrooms.c.user_id == user_id)
            
        if name is not None:
            stmt = stmt.where(Classrooms.name == name)
            
        if classroom_id is not None:
            stmt = stmt.where(Classrooms.id == classroom_id)
            
        reslut = await self.session.execute(stmt)
        res = reslut.scalar()
        return res > 0
    
    async def get_teacher_classrooms(self, teacher_id: uuid.UUID):
        stmt = (
            select(
                Classrooms.id.label("classroom_id"),
                Classrooms.name.label("classroom_name"),
                Users.id.label("student_id"),
                func.concat(Users.first_name, " ", Users.last_name).label("student_name")
            )
            .outerjoin(teachers_students, teachers_students.c.classroom_id == Classrooms.id)
            .outerjoin(Users, Users.id == teachers_students.c.student_id)
            .where(Classrooms.teacher_id == teacher_id)
            .order_by(Classrooms.id)
        )
        result = await self.session.execute(stmt)
        return result.mappings().all()
        

    # async def get_students(self, id: uuid.UUID):
    #     stmt = (
    #         select(
    #             func.concat(Users.first_name, " ", Users.last_name).label("student_name"),
    #             func.count(
    #                 func.nullif(Submissions.status != "verificated", )
    #             ),
    #             Submissions.status,
    #             Submissions.total_score,
    #             Tasks.title,
    #         )
    #         .where(Classrooms.id == id)
    #         .join(users_classrooms, Classrooms.id == users_classrooms.c.classroom_id)
    #         .join(Users, users_classrooms.c.user_id == Users.id)
    #         .where(Users.role == RoleUser.student)
    #         .join(Submissions, Users.id == Submissions.student_id)
    #         .join(Tasks, Submissions.task_id == Tasks.id)
    #     )
    #     response = await self.session.execute(stmt)
    #     rows = response.all()
    #     return rows



        