from unittest.mock import AsyncMock, Mock
from fastapi import HTTPException, status
import uuid
from fastapi import HTTPException
import pytest

from app.models.model_classroom import Classrooms
from app.models.model_users import Users
from app.services.service_classroom import ServiceClassroom
from app.utils.password import get_password_hash

@pytest.fixture(scope="function")
def teacher() -> Users:
    return Users(
        id=uuid.uuid4(),
        first_name="Иван",
        last_name="Иванов",
        email="ivan@example.com",
        password=get_password_hash("123456"),
        role="teacher",
        is_verificated=True
    )
    
@pytest.fixture(scope="function")
def classroom() -> Classrooms:
    return Classrooms(
        id=uuid.uuid4(),
        name='A1'
    )

@pytest.fixture(scope='module')
def mock_service():
    mock_session = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.flush = AsyncMock()
    
    return ServiceClassroom(session=mock_session)


@pytest.mark.asyncio
async def test_create_success(teacher, mock_service, monkeypatch):
    monkeypatch.setattr("app.services.service_classroom.RepoClassroom.exists", AsyncMock(return_value=False))
    monkeypatch.setattr("app.services.service_classroom.RepoTeacher.append_classroom", AsyncMock(return_value=None))
    
    result = await mock_service.create("A1", teacher)
    assert result.name == "A1"


@pytest.mark.asyncio
async def test_create_classroom_name_exists(teacher, mock_service, monkeypatch):
    monkeypatch.setattr("app.services.service_classroom.RepoClassroom.exists", AsyncMock(return_value=True))

    with pytest.raises(HTTPException) as exc:
        await mock_service.create("A1", teacher)
    
    assert exc.value.status_code == status.HTTP_409_CONFLICT
    assert exc.value.detail == "Class with this name already exists"


        
# @pytest.mark.asyncio
# async def test_get_all_success(monkeypatch):

# @pytest.mark.asyncio
# async def test_get_success(monkeypatch):

@pytest.mark.asyncio
async def test_update_success(mock_service, classroom, monkeypatch):
    monkeypatch.setattr("app.services.service_classroom.RepoClassroom.exists", AsyncMock(return_value=True))
    mock_service.session = AsyncMock(return_value=classroom)
    result = await mock_service.update(uuid.uuid4, "A2")
    assert result == {"message": "success"}


@pytest.mark.asyncio
async def test_update_classroom_name_exists(teacher, mock_service, monkeypatch):
    monkeypatch.setattr("app.services.service_classroom.RepoClassroom.exists", AsyncMock(return_value=True))

    with pytest.raises(HTTPException) as exc:
        await mock_service.create("A1", teacher)
    
    assert exc.value.status_code == status.HTTP_409_CONFLICT
    assert exc.value.detail == "Class with this name already exists"
    
    

@pytest.mark.asyncio
async def test_delete__classroom_name_exists(teacher, mock_service, monkeypatch):
    monkeypatch.setattr("app.services.service_classroom.RepoClassroom.exists", AsyncMock(return_value=True))

    with pytest.raises(HTTPException) as exc:
        await mock_service.create("A1", teacher)
    
    assert exc.value.status_code == status.HTTP_409_CONFLICT
    assert exc.value.detail == "Class with this name already exists"
