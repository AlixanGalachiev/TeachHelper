import pytest
import pytest_asyncio
from pprint import pprint
from sqlalchemy import insert


from app.models import User, Work, WorkStatus, Task, CreateWork, CreateTask, TaskType, Classroom, classroom_students
from app.repositories import TaskRepo, WorkRepo


@pytest.mark.asyncio
async def test_teacher_get_works(db_objects, session):
	repo = WorkRepo(session)

	# teacher_get_works
	# без фильтров
	result = await repo.teacher_get_works(teacher_id = teacher.id)
	row = result[0]
	assert row['first_name'] == 'Student'


	# по классам/ученикам
	result = await repo.teacher_get_works(teacher_id = teacher.id, class_name = 'classroom.name')
	assert result == []

	result = await repo.teacher_get_works(teacher_id = teacher.id, class_name = classroom.name)
	row = result[0]
	assert row['first_name'] == 'Student'
	assert row['middle_name'] == 'S'
	assert row['last_name'] == 'Test'

	result = await repo.teacher_get_works(teacher_id = teacher.id, student_id = 'd8b071bf-2a76-4a24-85f6-f8177326014a')
	assert result == []

	result = await repo.teacher_get_works(teacher_id = teacher.id, student_id = student.id)
	row = result[0]
	assert row['first_name'] == 'Student'
	assert row['middle_name'] == 'S'
	assert row['last_name'] == 'Test'


	# по статусам
	result = await repo.teacher_get_works(teacher_id = teacher.id, status = WorkStatus.draft)
	assert result == []

	result = await repo.teacher_get_works(teacher_id = teacher.id, status = WorkStatus.executing)
	assert row['first_name'] == 'Student'
	assert row['middle_name'] == 'S'
	assert row['last_name'] == 'Test'
	assert row['status']   == WorkStatus.executing


	# по 2 фильтрам

	result = await repo.teacher_get_works(teacher_id = teacher.id, status = WorkStatus.checking, student_id = student.id)
	assert result == []

	result = await repo.teacher_get_works(teacher_id = teacher.id, status = WorkStatus.executing, student_id = student.id)
	assert row['first_name'] == 'Student'
	assert row['middle_name'] == 'S'
	assert row['last_name'] == 'Test'
	assert row['status']   == WorkStatus.executing




	# student_get_works
	result = await repo.student_get_works(student_id = "d8b071bf-2a76-4a24-85f6-f8177326014a")
	assert result == []

	result = await repo.student_get_works(student_id = db_objects['student'].id)
	row = result[0]
	assert row.taskname == task.name


	# detail
	result = await repo.detail(work_id = "d8b071bf-2a76-4a24-85f6-f8177326014a")
	assert result == []

	result = await repo.detail(work_id = db_objects['work'].id)
	row = result[0]
	assert row.taskname == task.name
