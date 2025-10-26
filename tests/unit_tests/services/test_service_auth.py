import uuid
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import pytest
from unittest.mock import AsyncMock, patch, ANY, Mock
from pydantic import EmailStr
from app.models.model_users import Users
from app.schemas.schema_auth import UserRead, UserRegister
from app.services.service_auth import ServiceAuth
from app.utils.password import get_password_hash


@pytest.fixture(scope="function")
def user_db_verificated() -> Users:
    """Пользователь с подтверждённой почтой"""
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
def user_db_unverificated() -> Users:
    """Пользователь без подтверждённой почты"""
    return Users(
        id=uuid.uuid4(),
        first_name="Иван",
        last_name="Иванов",
        email="ivan@example.com",
        password=get_password_hash("123456"),
        role="teacher",
        is_verificated=False
    )

@pytest.fixture(scope="function")
def user_register() -> UserRegister:
    """Пользователь на регистрацию"""
    return UserRegister(
        first_name="Иван",
        last_name="Иванов",
        email="ivan@example.com",
        password="123456",
        role="teacher"
    )

@pytest.fixture(scope="function")
def form_data():
    return OAuth2PasswordRequestForm(username="ivan@example.com", password="123456")

@pytest.fixture(scope='function')
def mock_service():
    mock_session = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.commit = AsyncMock()
    
    return ServiceAuth(session=mock_session)
    
    

from dotenv import load_dotenv
load_dotenv()

@pytest.mark.asyncio(loop_scope="module")
async def test_register_success(user_register, user_db_unverificated, mock_service, monkeypatch):
    monkeypatch.setattr("app.services.service_auth.RepoUser.email_exists", AsyncMock(return_value=False))
    monkeypatch.setattr("app.services.service_auth.RepoUser.create", AsyncMock(return_value=user_db_unverificated))
    
    result = await mock_service.register(user_register)
    
    assert result == UserRead.model_validate(user_db_unverificated)

@pytest.mark.asyncio(loop_scope="module")
async def test_register_user_exists(user_register, mock_service, monkeypatch):
    monkeypatch.setattr("app.services.service_auth.RepoUser.email_exists", AsyncMock(return_value=True))
    
    with pytest.raises(HTTPException) as exc:
        await mock_service.register(user_register)
    
    assert exc.value.status_code == status.HTTP_409_CONFLICT
    assert exc.value.detail == "User with this email already exists"
    
@pytest.mark.asyncio(loop_scope="module")
async def test_login_success(user_db_verificated, form_data, mock_service, monkeypatch):
    monkeypatch.setattr("app.services.service_auth.RepoUser.email_exists", AsyncMock(return_value=True))
    monkeypatch.setattr("app.services.service_auth.RepoUser.get_by_email", AsyncMock(return_value=user_db_verificated))
    monkeypatch.setattr("app.services.service_auth.create_access_token", Mock(return_value="token"))
    result = await mock_service.login(form_data)
    
    assert result.access_token == "token"


@pytest.mark.asyncio(loop_scope="module")
async def test_login_user_not_exists(form_data, mock_service, monkeypatch):
    monkeypatch.setattr("app.services.service_auth.RepoUser.email_exists", AsyncMock(return_value=False))
    with pytest.raises(HTTPException) as exc:
        await mock_service.login(form_data)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "User with this email not exists"
    
    
@pytest.mark.asyncio(loop_scope="module")
async def test_login_wrong_password(user_db_verificated, form_data, mock_service, monkeypatch):
    monkeypatch.setattr("app.services.service_auth.RepoUser.email_exists", AsyncMock(return_value=True))
    monkeypatch.setattr("app.services.service_auth.RepoUser.get_by_email", AsyncMock(return_value=user_db_verificated))
    monkeypatch.setattr("app.services.service_auth.verify_password", Mock(return_value=False))
    
    with pytest.raises(HTTPException) as exc:
        await mock_service.login(form_data)

    assert exc.value.status_code== status.HTTP_401_UNAUTHORIZED
    assert exc.value.detail == "Incorrect password"

@pytest.mark.asyncio(loop_scope="module")
async def test_login_unverifed_user(user_db_unverificated, form_data, mock_service, monkeypatch):
    monkeypatch.setattr("app.services.service_auth.RepoUser.email_exists", AsyncMock(return_value=True))
    monkeypatch.setattr("app.services.service_auth.RepoUser.get_by_email", AsyncMock(return_value=user_db_unverificated))
    monkeypatch.setattr("app.services.service_auth.create_access_token", Mock(return_value="token"))

    with pytest.raises(HTTPException) as exc:
        await mock_service.login(form_data)
  
    assert exc.value.status_code== status.HTTP_403_FORBIDDEN
    assert exc.value.detail == "Please confirm your email first"
  


@pytest.mark.asyncio(loop_scope="module")
async def test_send_email_confirmation_link_success(user_db_unverificated, mock_service, monkeypatch):
    monkeypatch.setattr("app.services.service_auth.RepoUser.email_exists", AsyncMock(return_value=True))
    monkeypatch.setattr("app.services.service_auth.RepoUser.get_by_email", AsyncMock(return_value=user_db_unverificated))
    monkeypatch.setattr("app.services.service_auth.ServiceMail.send_mail_async", AsyncMock(return_value=None))

    result = await mock_service.send_email_confirmation_link(user_db_unverificated.email)
    
    assert result == {"message": "Письмо отправлено"}


@pytest.mark.asyncio(loop_scope="module")
async def test_send_email_confirmation_link_user_not_exists(form_data, mock_service, monkeypatch):
    monkeypatch.setattr("app.services.service_auth.RepoUser.email_exists", AsyncMock(return_value=False))

    with pytest.raises(HTTPException) as exc:
        await mock_service.login(form_data)
  
    assert exc.value.status_code== status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "User with this email not exists"

@pytest.mark.asyncio(loop_scope="module")
async def test_send_email_confirmation_link_user_verified(user_db_verificated, mock_service, monkeypatch):
    monkeypatch.setattr("app.services.service_auth.RepoUser.email_exists", AsyncMock(return_value=True))
    monkeypatch.setattr("app.services.service_auth.RepoUser.get_by_email", AsyncMock(return_value=user_db_verificated))

    with pytest.raises(HTTPException) as exc:
        await mock_service.send_email_confirmation_link(user_db_verificated.email)
  
    assert exc.value.status_code== status.HTTP_409_CONFLICT
    assert exc.value.detail == "User is already verificated"


@pytest.mark.asyncio(loop_scope="module")
async def test_confirm_email_success(user_db_unverificated, mock_service, monkeypatch):
    monkeypatch.setattr("app.services.service_auth.decode_token", Mock(return_value={"email": user_db_unverificated.email}))
    monkeypatch.setattr("app.services.service_auth.RepoUser.get_by_email", AsyncMock(return_value=user_db_unverificated))
    
    result = await mock_service.confirm_email("Bearer token")
    assert result ==  {"message": "Почта подтверждена"}
    

@pytest.mark.asyncio(loop_scope="module")
async def test_confirm_email_invalid_token(user_db_unverificated, mock_service, monkeypatch):
    monkeypatch.setattr("app.services.service_auth.decode_token", Mock(return_value={"wrong": user_db_unverificated.email}))

    with pytest.raises(HTTPException) as exc:
        await mock_service.confirm_email("Bearer token")
  
    assert exc.value.status_code== status.HTTP_400_BAD_REQUEST
    assert exc.value.detail == "Invalid token"

@pytest.mark.asyncio(loop_scope="module")
async def test_confirm_email_user_not_exists(user_db_unverificated, mock_service, monkeypatch):
    monkeypatch.setattr("app.services.service_auth.decode_token", Mock(return_value={"email": user_db_unverificated.email}))
    monkeypatch.setattr("app.services.service_auth.RepoUser.get_by_email", AsyncMock(return_value=None))

    with pytest.raises(HTTPException) as exc:
        await mock_service.confirm_email("Bearer token")
  
    assert exc.value.status_code== status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "User with this email not exists"

@pytest.mark.asyncio(loop_scope="module")
async def test_forgot_password_success(user_db_verificated, mock_service, monkeypatch):
    monkeypatch.setattr("app.services.service_auth.RepoUser.email_exists", AsyncMock(return_value=True))
    monkeypatch.setattr("app.services.service_auth.RepoUser.get_by_email", AsyncMock(return_value=user_db_verificated))
    monkeypatch.setattr("app.services.service_auth.ServiceMail.send_mail_async", AsyncMock(return_value=None))

    result = await mock_service.forgot_password(user_db_verificated.email)
    
    assert result == {"message": "Письмо отправлено"}


@pytest.mark.asyncio(loop_scope="module")
async def test_forgot_password_user_not_exists(user_db_verificated, mock_service, monkeypatch):
    monkeypatch.setattr("app.services.service_auth.RepoUser.email_exists", AsyncMock(return_value=False))

    with pytest.raises(HTTPException) as exc:
        await mock_service.forgot_password(user_db_verificated.email)
  
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "User with this email not exists"


@pytest.mark.asyncio(loop_scope="module")
async def test_forgot_password_user_unverified(user_db_unverificated, mock_service, monkeypatch):
    monkeypatch.setattr("app.services.service_auth.RepoUser.email_exists", AsyncMock(return_value=True))
    monkeypatch.setattr("app.services.service_auth.RepoUser.get_by_email", AsyncMock(return_value=user_db_unverificated))
    monkeypatch.setattr("app.services.service_auth.ServiceMail.send_mail_async", AsyncMock(return_value=None))

    with pytest.raises(HTTPException) as exc:
        await mock_service.forgot_password(user_db_unverificated.email)
  
    assert exc.value.status_code== status.HTTP_403_FORBIDDEN
    assert exc.value.detail == "Please confirm your email first"




@pytest.mark.asyncio(loop_scope="module")
async def test_reset_password_success(user_db_verificated, mock_service, monkeypatch):
    monkeypatch.setattr("app.services.service_auth.decode_token", Mock(return_value={"email": user_db_verificated.email}))
    monkeypatch.setattr("app.services.service_auth.RepoUser.get_by_email", AsyncMock(return_value=user_db_verificated))
    
    result = await mock_service.confirm_email("Bearer token")
    assert result ==  {"message": "Почта подтверждена"}
    

@pytest.mark.asyncio(loop_scope="module")
async def test_reset_password_invalid_token(user_db_verificated, mock_service, monkeypatch):
    monkeypatch.setattr("app.services.service_auth.decode_token", Mock(return_value={"wrong": user_db_verificated.email}))

    with pytest.raises(HTTPException) as exc:
        await mock_service.confirm_email("Bearer token")
  
    assert exc.value.status_code== status.HTTP_400_BAD_REQUEST
    assert exc.value.detail == "Invalid token"

@pytest.mark.asyncio(loop_scope="module")
async def test_reset_password_user_not_exists(user_db_unverificated, mock_service, monkeypatch):
    monkeypatch.setattr("app.services.service_auth.decode_token", Mock(return_value={"email": user_db_unverificated.email}))
    monkeypatch.setattr("app.services.service_auth.RepoUser.get_by_email", AsyncMock(return_value=None))

    with pytest.raises(HTTPException) as exc:
        await mock_service.confirm_email("Bearer token")
  
    assert exc.value.status_code== status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "User with this email not exists"