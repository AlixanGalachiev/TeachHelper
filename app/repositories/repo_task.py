import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.model_task import Task
from sqlalchemy import select

class TaskRepo:

	def __init__(self, session: AsyncSession):
		self.session = session

	async def get_all(
		self: AsyncSession,
		teacher_id: uuid.UUID,
		offset: int = 0,
		limit: int = 10
	):
		stmt = (
			select(Task)
			.where(Task.teacher_id == teacher_id)
			.order_by(Task.updated_at)
			.offset(offset)
			.limit(limit)
		)
		result = await self.session.execute(stmt)
		rows = result.scalars().all()
		return rows

