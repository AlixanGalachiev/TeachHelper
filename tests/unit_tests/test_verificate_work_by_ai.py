from asyncio import Task
import os
import uuid
import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from app.db import get_sync_session
from app.models.model_user import User
from app.routes.route_work import verificate_work_by_ai
from app.models.model_work import Work, WorkStatus

# Фикстура для студента
@pytest.fixture
def mock_student(session):
	user = User(
		id=uuid.uuid4(),
		name="test_student",
		email="student@example.com",
		first_name="Ivan",
		middle_name="Ivanovich",
		role="student",
		password_hash="hashed_password_123"
	)
	session.add(user)
	session.commit()
	return user

# Фикстура для преподавателя
@pytest.fixture
def mock_teacher(session):
	teacher = User(
		id=uuid.uuid4(),
		name="test_teacher",
		email="teacher@example.com",
		first_name="Petr",
		middle_name="Petrovich",
		role="teacher",
		password_hash="hashed_password_456"
	)
	session.add(teacher)
	session.commit()
	return teacher

# Фикстура для задачи (Task)
@pytest.fixture
def mock_task(session, mock_teacher):
	task = Task(
		id=uuid.uuid4(),
		name="Test Task",
		type="homework",
		max_point=100,
		teacher_id=mock_teacher.id
	)
	session.add(task)
	session.commit()
	return task

# Фикстура для Work, связанного с студентом и задачей
@pytest.fixture
def mock_work(session, mock_student, mock_task):
	work = Work(
		id=uuid.uuid4(),
		images=["image1.png", "image2.png"],
		verifed_by_ai=False,
		status=WorkStatus.in_work,
		student_id=mock_student.id,
		task_id=mock_task.id
	)
	session.add(work)
	session.commit()
	return work




# def verificate_work_by_ai(work_id: uuid.UUID):
# 	with get_sync_session() as session:
# 		work = session.get(Work, work_id)
# 		handle_results = handle_images(work.images)

# 		for img_path, image in handle_results:
# 			cv2.imwrite(f"{os.getenv('WORK_ERROR_IMAGES')}/{os.path.basename(img_path)}", image)

# 		work.verifed_by_ai = True
# 		session.commit()


def test_verificate_work_by_ai(monkeypatch, mock_work, tmp_path):
	monkeypatch.setenv(("WORK_ERROR_IMAGES"), str(tmp_path))

	mock_images = [
		("image1.png", np.zeros((10, 10, 3), dtype=np.uint8)),
		("image2.png", np.ones((20, 20, 3), dtype=np.uint8)),
	]


	with patch("app.db.get_sync_session") as mock_session, \
		patch("app.services.HTRService.trOCR_recognition.handle_images", return_value=mock_images) as mock_handle, \
		patch("app.routes.route_work.cv2.inwrite", return_value=True) as mock_inwrite:

		session_mock = MagicMock()
		session_mock.get.return_value = mock_work
		mock_session.return_value.__enter__.return_value = session_mock


		verificate_work_by_ai(mock_work.id)

		mock_handle.assert_called_once_with(mock_work.images)


		assert mock_inwrite.call_count == 2
		called_paths = [c.args[0] for c in mock_inwrite.call_args_list]
		assert all(str(tmp_path) in p for p in called_paths)


		assert mock_work.verifed_by_ai is True


		session_mock.commit.assert_called_once()

