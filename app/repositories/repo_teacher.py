

import uuid
from fastapi import HTTPException, status
from sqlalchemy import insert, select

from app.models.model_classroom import Classrooms
from app.models.model_users import Users


class RepoTeacher:
    def __init__(self, session):
        self.session = session

    async def get_classrooms(self, teacher: Users):
        stmt = (
            select(Classrooms)
            .where(Classrooms.teacher_id == teacher.id)
        )
        result = await self.session.execute(stmt)
            
        return result.scalars().all()

    async def append_classroom(self, teacher_id: uuid.UUID, classroom_id: uuid.UUID):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Updated db backenders must redone their code")
        # stmt = insert(users_classrooms).values(
        #     user_id=teacher_id,
        #     classroom_id=classroom_id
        # )
        
        # result = await self.session.execute(stmt)
        return {"result"}
