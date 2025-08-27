# tests/test_repo_classroom.py
import pytest
from app.repositories.repo_classroom import ClassroomRepo, classroom_students
from app.models.model_classroom import Classroom
from sqlalchemy import select, insert
import time

@pytest.mark.asyncio
async def test_classroom_repo(users, session):
	"""
	Тестируем ClassroomRepo: create, add_student, get, rename
	"""
	teacher = users["teacher"]
	student = users["student"]

	repo = ClassroomRepo(session)

	# --- create ---
	classroom = await repo.create(name="Math 101", teacher_id=teacher.id)
	await session.flush()
	assert classroom.id is not None
	assert classroom.name == "Math 101"
	assert classroom.teacher_id == teacher.id

	# --- get ---
	classroom_from_db = await repo.get(classroom.id)
	assert classroom_from_db is not None
	assert classroom_from_db.name == "Math 101"


	classroom.students.append(student)
	await session.flush()

	result = await repo.get(classroom.id)
	classroom1 = await session.get(Classroom, classroom.id)
	

	# Проверим, что студент добавился
	classroom_with_student = await repo.get(classroom.id)
	students = classroom_with_student.students
	assert students[0].id == student.id

