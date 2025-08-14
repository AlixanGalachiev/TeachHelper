from typing import Sequence
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.model_homework import ErrorItem


class ErrorRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_for_homework(self, homework_id: int) -> Sequence[ErrorItem]:
        res = await self.session.execute(select(ErrorItem).where(ErrorItem.homework_id == homework_id))
        return res.scalars().all()

    async def delete_for_homework(self, homework_id: int) -> None:
        await self.session.execute(delete(ErrorItem).where(ErrorItem.homework_id == homework_id))
