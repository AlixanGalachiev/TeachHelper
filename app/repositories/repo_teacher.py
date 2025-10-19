

import uuid
from sqlalchemy import insert, select
from sqlalchemy.orm import selectinload

from app.models.model_users import Users, users_classrooms


class RepoTeacher:
    def __init__(self, session):
        self.session = session

    async def get_classrooms(self, teacher: Users):
        stmt = (
            select(Users)
            .options(selectinload(Users.classrooms))
            .where(Users.id == teacher.id)
        )
        result = await self.session.execute(stmt)
            
        teacher = result.scalar_one()
        return teacher.classrooms

    async def append_classroom(self, teacher_id: uuid.UUID, classroom_id: uuid.UUID):
        stmt = insert(users_classrooms).values(
            user_id=teacher_id,
            classroom_id=classroom_id
        )
        
        result = await self.session.execute(stmt)
        return result
