from typing import Optional, Sequence, List
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.model_homework import Homework, ErrorItem


class HomeworkRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, student_id: int, classroom_id: int | None, file_path: str | None, recognized_text: str | None) -> Homework:
        hw = Homework(
            student_id=student_id,
            classroom_id=classroom_id,
            file_path=file_path,
            recognized_text=recognized_text,
        )
        self.session.add(hw)
        await self.session.flush()
        return hw

    async def get(self, homework_id: int) -> Optional[Homework]:
        res = await self.session.execute(select(Homework).where(Homework.id == homework_id))
        return res.scalar_one_or_none()

    async def get_with_errors(self, homework_id: int) -> Optional[Homework]:
        res = await self.session.execute(
            select(Homework).options(selectinload(Homework.errors)).where(Homework.id == homework_id)
        )
        return res.scalar_one_or_none()

    async def list(self, student_id: Optional[int] = None, classroom_id: Optional[int] = None, limit: int = 100, offset: int = 0) -> Sequence[Homework]:
        stmt = select(Homework)
        if student_id is not None:
            stmt = stmt.where(Homework.student_id == student_id)
        if classroom_id is not None:
            stmt = stmt.where(Homework.classroom_id == classroom_id)
        res = await self.session.execute(stmt.offset(offset).limit(limit))
        return res.scalars().all()

    async def update(self, homework_id: int, **fields) -> Optional[Homework]:
        await self.session.execute(update(Homework).where(Homework.id == homework_id).values(**fields))
        await self.session.flush()
        return await self.get(homework_id)

    async def delete(self, homework_id: int) -> None:
        await self.session.execute(delete(Homework).where(Homework.id == homework_id))

    async def add_errors(self, homework_id: int, items: List[dict]) -> None:
        for item in items:
            err = ErrorItem(homework_id=homework_id, **item)
            self.session.add(err)
        await self.session.flush()
