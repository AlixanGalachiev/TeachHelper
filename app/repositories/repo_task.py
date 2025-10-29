from time import time
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models.model_tasks import Exercises, Tasks

class RepoTasks():
    def __init__(self, session: AsyncSession):
        self.session = session


    async def get(self, id: uuid.UUID):
        stmt = (
            select(Tasks)
            .where(Tasks.id == id)
            .options(
                selectinload(Tasks.exercises)
                .selectinload(Exercises.criterions)
            )
        )
        response = await self.session.execute(stmt)
        return response.scalars().first()