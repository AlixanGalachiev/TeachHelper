

class TaskRepo:

	def __init__(self, session: AsyncSession):
		self.session = session

	async def detail(
		self: AsyncSession,
		task_id: uuid.UUID
	):
		task = await self.session.get(Task, task_id)
		if not task:
			raise HTTPException(404, message="This work doesn't exists")

		return task


	async def get_all(
		self: AsyncSession,
		teacher_id: uuid.UUID,
		offset: int = 0,
		limit: int = 10
	)
		stmt = (
			select(Task)
			.where(Task.teacher_id == teacher_id)
			.group_by(Task.updated_at)
			.offset(offset)
			.limit(limit)
		)
		result = await self.session.execute(stmt)
		rows = result.scalars.all()
		return rows

	
	async def update(
		self,
		task_id: uuid.UUID,
		updates: TaskUpdate
	):
		task = await self.session.get(Task, task_id)
		if not task:
			raise HTTPException(404, message="This task doesn't exist")

		# обновляем только те поля, которые переданы
		for field, value in updates.dict(exclude_unset=True).items():
			setattr(task, field, value)

		await self.session.flush()  # сохраняем изменения
		return task


	async def delete(self, task_id: uuid.UUID):
		task = await self.session.get(Task, task_id)
		if not task:
			raise HTTPException(404, message="This task doesn't exist")

		await self.session.delete(task)
		await self.session.flush()
		return task


