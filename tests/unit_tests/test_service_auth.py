import uuid
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import pytest
from unittest.mock import AsyncMock, patch, ANY, Mock
from pydantic import EmailStr
from app.models.model_users import Users
from app.schemas.schema_auth import UserRead, UserRegister, UserToken
from app.services.service_auth import ServiceAuth
from app.services.service_mail import ServiceMail
from app.utils import password


import os
from dotenv import load_dotenv
load_dotenv()

@pytest.mark.asyncio
@patch("app.services.service_user.ServiceMail.send_mail_async", new_callable=AsyncMock)
async def test_validate_email(mock_service_mail):
    service = ServiceAuth(session=None)
    email: EmailStr = "test@example.com"
    
    result = await service.validate_email(email)
    
    mock_service_mail.assert_awaited_once_with(
        email,
        "Подтверждение почты",
        "template_verification_code.html",
        ANY
    )
    
    assert result == {"message": "Код отправлен на почту"}


@pytest.mark.asyncio
async def test_register(monkeypatch):
    repo_mock = AsyncMock()
    repo_mock.email_exists = AsyncMock(return_value=False)
    
    mock_user = Users(
        id=uuid.uuid4(),
        first_name="Иван",
        last_name="Иванов",
        email="ivan@example.com",
        password="hashed",
        role="teacher"
    )
    repo_mock.create = AsyncMock(side_effect=lambda user: mock_user)

    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()

    monkeypatch.setattr("app.services.service_user.UserRepo", lambda session: repo_mock)
    
    service = ServiceAuth(mock_session)
    user_data = UserRegister(
        first_name="Иван",
        last_name="Иванов",
        email="ivan@example.com",
        password="123456",
        role="teacher"
    )
    
    result = await service.register(user_data)

    repo_mock.email_exists.assert_awaited_once_with("ivan@example.com")
    repo_mock.create.assert_awaited_once()
    mock_session.commit.assert_awaited_once()
    assert result.email == "ivan@example.com"


@pytest.mark.asyncio
async def test_register_email_exists(monkeypatch):
    repo_mock = AsyncMock()
    repo_mock.email_exists = AsyncMock(return_value=True)
    mock_session = AsyncMock()
    monkeypatch.setattr("app.services.service_user.UserRepo", lambda session: mock_session)
    
    service = ServiceAuth(mock_session)
    user_data = UserRegister(
        first_name="Иван",
        last_name="Иванов",
        email="ivan@example.com",
        password="123456",
        role="teacher"
    )
    with pytest.raises(HTTPException) as exc:
        await service.register(user_data)

    assert exc.value.status_code == 409
    assert exc.value.detail == "User with this email already exists"


@pytest.mark.asyncio
async def test_login(monkeypatch):
    repo_mock = Mock()
    repo_mock.email_exists = AsyncMock(return_value=True)
    form_data = OAuth2PasswordRequestForm(username="ivan@example.com", password="123456")
    db_user = Users(
        id=uuid.uuid4(),
        first_name="Иван",
        last_name="Иванов",
        email="ivan@example.com",
        password=password.get_password_hash(form_data.password),
        role="teacher"
    )
    repo_mock.get_by_email = AsyncMock(side_effect=lambda email: db_user)
    # repo_mock.get_by_email.return_value = db_user

    mock_session = AsyncMock()
    monkeypatch.setattr("app.services.service_user.UserRepo", lambda session: repo_mock)
    monkeypatch.setattr("app.services.service_user.verify_password", lambda password, hashed_password: True)

    monkeypatch.setattr("app.services.service_user.create_access_token", lambda data: "lal")

    
    service = ServiceAuth(mock_session)
    result = await service.login(form_data)
    
    assert result == UserToken(token_type="Bearer", access_token='lal')

@pytest.mark.asyncio
async def test_login_email_not_exists(monkeypatch):
    repo_mock = Mock()
    repo_mock.email_exists = AsyncMock(return_value=False)
    mock_session = AsyncMock()
    form_data = OAuth2PasswordRequestForm(username="ivan@example.com", password="123456")
    
    
    monkeypatch.setattr("app.services.service_user.UserRepo", lambda session: repo_mock)
    service = ServiceAuth(mock_session)
    with pytest.raises(HTTPException) as exc:
        await service.login(form_data)
    assert exc.value.detail == "User with this email not exists"
    assert exc.value.status_code == 409

@pytest.mark.asyncio
async def test_login_wrong_password(monkeypatch):
    repo_mock = AsyncMock()
    repo_mock.email_exists = AsyncMock(return_value=True)
    form_data = OAuth2PasswordRequestForm(username="ivan@example.com", password="123456")
    db_user = Users(
        id=uuid.uuid4(),
        first_name="Иван",
        last_name="Иванов",
        email="ivan@example.com",
        password=password.get_password_hash("1234567"),
        role="teacher"
    )
    repo_mock.get_by_email = AsyncMock(side_effect=lambda email: db_user)
    mock_session = AsyncMock()
    monkeypatch.setattr("app.services.service_user.UserRepo", lambda session: repo_mock)
    
    
    service = ServiceAuth(mock_session)
    with pytest.raises(HTTPException) as exc:
        await service.login(form_data)

    assert exc.value.detail == "Incorrect password"
    assert exc.value.status_code == 401

    
    
@pytest.mark.asyncio
@patch("app.services.service_user.ServiceMail.send_mail_async", new_callable=AsyncMock)
async def test_send_reset_mail(send_mail_async_mock, monkeypatch):
    repo_mock = AsyncMock()
    repo_mock.email_exists = AsyncMock(return_value=True)
    email: EmailStr = "ivan@example.com"
    db_user = Users(
        id=uuid.uuid4(),
        first_name="Иван",
        last_name="Иванов",
        email="ivan@example.com",
        password=password.get_password_hash("1234567"),
        role="teacher"
    )
    repo_mock.get_by_email = AsyncMock(side_effect=lambda email: db_user)
    monkeypatch.setattr("app.services.service_user.create_access_token", lambda session, exp: "hash")
    monkeypatch.setattr("app.services.service_user.UserRepo", lambda session: repo_mock)

    
    session_mock = AsyncMock()
    service = ServiceAuth(session_mock)
    result = await service.send_reset_mail(email)
    send_mail_async_mock.assert_awaited_once()
    assert result == {"message": "Письмо отправленно"}


@pytest.mark.asyncio
@patch("app.services.service_user.ServiceMail.send_mail_async", new_callable=AsyncMock)
async def test_send_reset_mail_not_exists(send_mail_async_mock, monkeypatch):
    repo_mock = AsyncMock()
    repo_mock.email_exists = AsyncMock(return_value=False)
    email: EmailStr = "hahaha@example.com"
    monkeypatch.setattr("app.services.service_user.UserRepo", lambda session: repo_mock)

    
    session_mock = AsyncMock()
    service = ServiceAuth(session_mock)
    with pytest.raises(HTTPException) as exc:
        await service.send_reset_mail(email)

    assert exc.value.status_code == 409
    assert exc.value.detail == "User with this email not exists"
    send_mail_async_mock.assert_not_awaited()
