# tests/test_repo_task.py
import pytest
from app.repositories.repo_task import TaskRepo
from app.models.model_task import Task, TaskType


@pytest.mark.asyncio
async def test_task_repo(users, session):

	teacher = users["teacher"]
	student = users["student"]
	
	repo = TaskRepo(session)


	task = Task(
		name = "Task 101",
		type = TaskType.dictation,
		max_point = 10,
		description = "Task 101 description",
		teacher_id = teacher.id
	)

	session.add(task)
	await session.flush()


	teacher_tasks = await repo.get_all(teacher.id)
	assert teacher_tasks[0].id == task.id



	
