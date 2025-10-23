
import asyncio
from datetime import timedelta
from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from sqlalchemy import select

from app.config.config_app import settings
from app.models.model_users import Users
from app.utils.oAuth import create_access_token
from main import app
from app.schemas.schema_auth import UserRead, UserRegister

@pytest_asyncio.fixture(scope="function")
def user_register() -> UserRegister:
    """Пользователь на регистрацию"""
    return UserRegister(
        first_name="Иван",
        last_name="Иванов",
        email="ivan@example.com",
        password="123456",
        role="teacher"
    )

@pytest_asyncio.fixture(scope="function")
def user_not_exitsts() -> UserRegister:
    """Пользователь на регистрацию"""
    return UserRegister(
        first_name="Иван",
        last_name="Иванов",
        email="empty@example.com",
        password="123456",
        role="teacher"
    )


@pytest.mark.asyncio(loop_scope="session")
async def test_auth(client, user_register):
    response = await client.post("/auth/register", json=user_register.model_dump())
    data = response.json()

    assert response.status_code == 200
    assert data["first_name"] == user_register.first_name
    assert data["last_name"] == user_register.last_name
    assert data["email"] == user_register.email
    assert data["role"] == user_register.role


@pytest.mark.asyncio(loop_scope="session")
async def test_login(client, user_register):
    response = await client.post("/auth/login",
        headers = {"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "username": user_register.email,
            "password": user_register.password
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Please confirm your email first"


@pytest.mark.asyncio(loop_scope="session")
async def test_send_email_confirmation_link(client, user_register):
    response = await client.post(
        "/auth/send_email_confirmation_link",
        json={"email": user_register.email}
    )

    response.status_code == 200
    response.json() == {"message": "Письмо отправлено"}

@pytest.mark.asyncio(loop_scope="session")
async def test_confirm_email(client, user_register):
    token = create_access_token({"email": user_register.email}, settings.SECRET_CONFIRM_KEY, timedelta(seconds=100))
    response = await client.post(
        "/auth/confirm_email",
        params={'token': f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Почта подтверждена"}
    
@pytest.mark.asyncio(loop_scope="session")
async def test_forgot_password(client, user_register):
    response = await client.post(
        "/auth/forgot_password",
        json={"email": user_register.email}
    )
    
    response.status_code == 200
    response.json() == {"message": "Письмо отправлено"}

@pytest.mark.asyncio(loop_scope="session")
async def test_reset_password(client, user_register):
    token = create_access_token({"email": user_register.email}, settings.SECRET_RESET_KEY, timedelta(seconds=100))
    response = await client.post(
        "/auth/reset_password",
        json= {
            'password': "123456",
            'token': f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Пароль обновлён"}

@pytest.mark.asyncio(loop_scope="session")
async def test_me(client, user_register):
    token = create_access_token({"email": user_register.email}, settings.SECRET)
    response = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Иван"
    assert data["last_name"] == "Иванов"
    assert data["email"] == "ivan@example.com"
    assert data["role"] == "teacher"


@pytest.mark.asyncio(loop_scope="session")
async def test_delete(client, user_register):
    token = create_access_token({"email": user_register.email}, settings.SECRET)
    response = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    
    user = response.json()
    print(user)

    token = create_access_token({"email": user_register.email}, settings.SECRET)
    response = await client.delete(
        f"/auth/{user["id"]}",
        headers={"Authorization": f"Bearer {token}"},
        params={"email": user['email']}
    )

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


