import uuid
import pytest
from unittest.mock import AsyncMock, Mock
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from app.models.model_users import Users
from app.services.teacher.service_students import ServiceStudents

@pytest.fixture(scope='module')
def teacher_user() -> Users:
    return Users(id=uuid.uuid4(), first_name="Иван", last_name="Иванов", role="teacher")

@pytest.fixture(scope='function')
def student_id():
    return uuid.uuid4()

@pytest.fixture(scope='function')
def classroom_id():
    return uuid.uuid4()

@pytest.fixture(scope='module')
def mock_service_students():
    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    return ServiceStudents(session=mock_session)

@pytest.mark.asyncio
async def test_move_to_class_student_not_exists(mock_service_students, teacher_user, student_id, classroom_id, monkeypatch):
    monkeypatch.setattr("app.services.teacher.service_students.RepoStudents.exists", AsyncMock(return_value=False))
    with pytest.raises(HTTPException) as exc:
        await mock_service_students.move_to_class(student_id, classroom_id, teacher_user)
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "Студент не найден"

@pytest.mark.asyncio
async def test_move_to_class_student_already_in_class(mock_service_students, teacher_user, student_id, classroom_id, monkeypatch):
    monkeypatch.setattr("app.services.teacher.service_students.RepoStudents.exists", AsyncMock(return_value=True))
    monkeypatch.setattr("app.services.teacher.service_students.RepoStudents.user_exists_in_class", AsyncMock(return_value=True))
    with pytest.raises(HTTPException) as exc:
        await mock_service_students.move_to_class(student_id, classroom_id, teacher_user)
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.value.detail == "Студент уже находится в этом классе"

@pytest.mark.asyncio
async def test_move_to_class_success(mock_service_students, teacher_user, student_id, classroom_id, monkeypatch):
    monkeypatch.setattr("app.services.teacher.service_students.RepoStudents.exists", AsyncMock(return_value=True))
    monkeypatch.setattr("app.services.teacher.service_students.RepoStudents.user_exists_in_class", AsyncMock(return_value=False))
    monkeypatch.setattr("app.services.teacher.service_students.RepoStudents.move_to_class", AsyncMock(return_value=None))

    result = await mock_service_students.move_to_class(student_id, classroom_id, teacher_user)
    assert isinstance(result, JSONResponse)
    assert result.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_remove_from_class_student_not_exists(mock_service_students, teacher_user, student_id, classroom_id, monkeypatch):
    monkeypatch.setattr("app.services.teacher.service_students.RepoStudents.exists", AsyncMock(return_value=False))
    with pytest.raises(HTTPException) as exc:
        await mock_service_students.remove_from_class(student_id, classroom_id, teacher_user)
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "Студент не найден"

@pytest.mark.asyncio
async def test_remove_from_class_student_not_in_class(mock_service_students, teacher_user, student_id, classroom_id, monkeypatch):
    monkeypatch.setattr("app.services.teacher.service_students.RepoStudents.exists", AsyncMock(return_value=True))
    monkeypatch.setattr("app.services.teacher.service_students.RepoStudents.user_exists_in_class", AsyncMock(return_value=False))
    with pytest.raises(HTTPException) as exc:
        await mock_service_students.remove_from_class(student_id, classroom_id, teacher_user)
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "Студент не состоит в этом классе"

@pytest.mark.asyncio
async def test_remove_from_class_success(mock_service_students, teacher_user, student_id, classroom_id, monkeypatch):
    monkeypatch.setattr("app.services.teacher.service_students.RepoStudents.exists", AsyncMock(return_value=True))
    monkeypatch.setattr("app.services.teacher.service_students.RepoStudents.user_exists_in_class", AsyncMock(return_value=True))
    monkeypatch.setattr("app.services.teacher.service_students.RepoStudents.remove_from_class", AsyncMock(return_value=None))

    result = await mock_service_students.remove_from_class(student_id, classroom_id, teacher_user)
    assert isinstance(result, JSONResponse)
    assert result.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_delete_student_not_exists(mock_service_students, teacher_user, student_id, monkeypatch):
    monkeypatch.setattr("app.services.teacher.service_students.RepoStudents.exists", AsyncMock(return_value=False))
    with pytest.raises(HTTPException) as exc:
        await mock_service_students.delete(student_id, teacher_user)
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "Студент не найден"

@pytest.mark.asyncio
async def test_delete_student_success(mock_service_students, teacher_user, student_id, monkeypatch):
    monkeypatch.setattr("app.services.teacher.service_students.RepoStudents.exists", AsyncMock(return_value=True))
    monkeypatch.setattr("app.services.teacher.service_students.RepoStudents.delete", AsyncMock(return_value=None))

    result = await mock_service_students.delete(student_id, teacher_user)
    assert isinstance(result, JSONResponse)
    assert result.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_get_performans_data_student_not_exists(mock_service_students, teacher_user, student_id, monkeypatch):
    monkeypatch.setattr("app.services.teacher.service_students.RepoStudents.exists", AsyncMock(return_value=False))
    with pytest.raises(HTTPException) as exc:
        await mock_service_students.get_performans_data(student_id, teacher_user)
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "Студент не найден"

@pytest.mark.asyncio
async def test_get_performans_data_success(mock_service_students, teacher_user, student_id, monkeypatch):
    monkeypatch.setattr("app.services.teacher.service_students.RepoStudents.exists", AsyncMock(return_value=True))
    mock_data = {
        "agg_data": {},
        "works_data": []
    }
    monkeypatch.setattr("app.services.teacher.service_students.RepoStudents.get_performans_data", AsyncMock(return_value=mock_data))

    result = await mock_service_students.get_performans_data(student_id, teacher_user)
    assert result == {}
