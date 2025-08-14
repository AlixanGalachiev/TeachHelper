# tests/test_user_api.py
import pytest
from httpx import AsyncClient
from app.models.model_user import Role

@pytest.mark.asyncio
async def test_create_user_api(async_client: AsyncClient):
    payload = {
        "email": "apiuser@example.com",
        "password": "password123",
        "full_name": "API User",
        "role": Role.teacher.value
    }

    resp = await async_client.post("/users", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == payload["email"]
    assert data["full_name"] == payload["full_name"]

@pytest.mark.asyncio
async def test_duplicate_email(async_client: AsyncClient):
    payload = {
        "email": "dup@example.com",
        "password": "password123",
        "full_name": "Dup User",
        "role": Role.teacher.value
    }
    # Первый раз должно пройти
    resp1 = await async_client.post("/users", json=payload)
    assert resp1.status_code == 201

    # Второй раз должно вернуть 400
    resp2 = await async_client.post("/users", json=payload)
    assert resp2.status_code == 400
    assert "Email already registered" in resp2.text
