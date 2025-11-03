

import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload, load_only

from app.models.model_classroom import Classrooms
from app.models.model_users import Users, teachers_students


class RepoClassroom():
    def __init__(self, session):
        self.session = session

    async def exists(self, name: str|None = None, classroom_id: uuid.UUID|None = None, user_id: uuid.UUID|None = None):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Updated db backenders must redone their code")
        # stmt = select(func.count()).select_from(Classrooms)
        
        # if user_id is not None:
        #     stmt = stmt.join(users_classrooms, Classrooms.id == users_classrooms.c.classroom_id)
        #     stmt = stmt.where(users_classrooms.c.user_id == user_id)
            
        # if name is not None:
        #     stmt = stmt.where(Classrooms.name == name)
            
        # if classroom_id is not None:
        #     stmt = stmt.where(Classrooms.id == classroom_id)
            
        # reslut = await self.session.execute(stmt)
        # res = reslut.scalar()
        return res > 0
    
    async def get_teacher_classrooms(self, teacher_id: uuid.UUID):
        stmt = (
            select(
                Classrooms.id,
                Classrooms.name
            )
            .where(Classrooms.teacher_id == teacher_id)
        )
        result = await self.session.execute(stmt)
        return result.mappings().all()
        

    # async def get_students(self, id: uuid.UUID):
    #     stmt = (
    #         select(
    #             func.concat(Users.first_name, " ", Users.last_name).label("student_name"),
    #             func.count(
    #                 func.nullif(Works.status != "verificated", )
    #             ),
    #             Works.status,
    #             Works.total_score,
    #             Tasks.title,
    #         )
    #         .where(Classrooms.id == id)
    #         .join(users_classrooms, Classrooms.id == users_classrooms.c.classroom_id)
    #         .join(Users, users_classrooms.c.user_id == Users.id)
    #         .where(Users.role == RoleUser.student)
    #         .join(Works, Users.id == Works.student_id)
    #         .join(Tasks, Works.task_id == Tasks.id)
    #     )
    #     response = await self.session.execute(stmt)
    #     rows = response.all()
    #     return rows


    # async def get_performans_data(self, student_id: uuid.UUID):
    #     agg_stmt = (
    #         select(
    #             Users.id.label("student_id"),
    #             func.concat(Users.first_name, " ", Users.last_name).label("student_name"),
    #             func.count().filter(Works.status == "verificated").label("verificated_works_count"),
    #             func.avg(Works.total_score).filter(Works.status == "verificated").label("avg_score"),
    #         )
    #         .where(Users.id == student_id)
    #         .outerjoin(Works, Users.id == Works.student_id)
    #         .group_by(Users.id, Users.first_name, Users.last_name)
    #     )
    #     agg_result = await self.session.execute(agg_stmt)
    #     agg_data = agg_result.mappings().all()

    #     works_stmt = (
    #         select(
    #             Works.id.label("submission_id"),
    #             Works.student_id.label('student_id'),
    #             Works.status,
    #             Works.total_score,
    #             Tasks.title.label("task_title"),
    #             Tasks.max_score
    #         )
    #         .join(Tasks, Works.task_id == Tasks.id)
    #         .where(Works.student_id == student_id)
    #     )
    #     works_result = await self.session.execute(works_stmt)
    #     works_data = works_result.mappings().all()
    #     return {
    #         "agg_data": agg_data,
    #         "works_data": works_data,
    #     }


        