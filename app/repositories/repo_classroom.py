from typing import Optional, Sequence
from sqlalchemy import select, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.model_classroom import Classroom, ClassroomStudent


class ClassroomRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, name: str, teacher_id: int) -> Classroom:
        classroom = Classroom(name=name, teacher_id=teacher_id)
        self.session.add(classroom)
        await self.session.flush()
        return classroom

    async def get(self, classroom_id: int) -> Optional[Classroom]:
        res = await self.session.execute(select(Classroom).where(Classroom.id == classroom_id))
        return res.scalar_one_or_none()

    async def list(self, teacher_id: Optional[int] = None, limit: int = 100, offset: int = 0) -> Sequence[Classroom]:
        stmt = select(Classroom)
        if teacher_id is not None:
            stmt = stmt.where(Classroom.teacher_id == teacher_id)
        res = await self.session.execute(stmt.offset(offset).limit(limit))
        return res.scalars().all()

    async def add_student(self, classroom_id: int, user_id: int) -> None:
        await self.session.execute(
            insert(ClassroomStudent).values(classroom_id=classroom_id, user_id=user_id)
        )
        await self.session.flush()

    async def remove(self, classroom_id: int) -> None:
        await self.session.execute(delete(Classroom).where(Classroom.id == classroom_id))
