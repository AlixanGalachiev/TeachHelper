import pytest
import pytest_asyncio
from pprint import pprint
from sqlalchemy import insert


from app.models import User, Work, WorkStatus, Task, CreateWork, CreateTask, TaskType, Classroom, classroom_students
from app.repositories import TaskRepo, WorkRepo
@pytest_asyncio.fixture()
async def db_objects(users, session):

	teacher = users["teacher"]
	student = users["student"]

	# создание задачи
	task_data = CreateTask(
		name       = "Task 101",
		type       = TaskType.dictation,
		max_point  = 10,
		teacher_id = teacher.id,
	)

	task = Task(**task_data.model_dump())
	session.add(task)
	await session.flush()


	# создание класса
	classroom = Classroom(name="class 1", teacher_id = teacher.id)
	session.add(classroom)
	await session.flush()
	await session.refresh(classroom)
	
	cr_sts_response = await session.execute(
		(insert(classroom_students)
		.values(
				student_id = student.id,
				classroom_id = classroom.id
			)
		.returning(classroom_students)
		)
	)
	cr_sts_rows = cr_sts_response.mappings().all()


	# создание работы
	work_data = CreateWork(
		files_url  =  'urllll',
		task_id    =  task.id,
		student_id =  student.id,
	)
	work = Work(**work_data.model_dump())
	work.status = WorkStatus.executing
	session.add(work)
	await session.commit()
	await session.refresh(task)
	await session.refresh(work)
	await session.refresh(student)
	return {
		"work": work,
		"task": task,
		"student": student,
		"teacher": teacher,
		"classroom": classroom,
		"cr_sts_rows": cr_sts_rows
	}
	




@pytest.mark.asyncio
async def test_teacher_get_works(db_objects, session):

	work        = db_objects['work']
	task        = db_objects['task']
	student     = db_objects['student']
	teacher     = db_objects['teacher']
	classroom   = db_objects['classroom']
	cr_sts_rows = db_objects['cr_sts_rows']

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
