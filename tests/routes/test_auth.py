import pytest
from app.schemas.schema_auth import UserCreate

@pytest.mark.asyncio
async def test_register_and_login(async_client):
    # --- Регистрация ---
    user_data = {
        "email": "student@test.com",
        "full_name": "Test Student",
        "role": "student",
        "password": "strongpassword"
    }
    response = await async_client.post("/auth/register", json=user_data)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["email"] == user_data["email"]
    assert "id" in json_data

    # --- Повторная регистрация должна вернуть ошибку ---
    response = await async_client.post("/auth/register", json=user_data)
    assert response.status_code == 400

    # --- Логин ---
    login_data = {
        "username": "student@test.com",  # OAuth2PasswordRequestForm использует username
        "password": "strongpassword"
    }
    response = await async_client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    # --- Логин с неверным паролем ---
    bad_login = {"username": "student@test.com", "password": "wrong"}
    response = await async_client.post("/auth/login", data=bad_login)
    assert response.status_code == 401
