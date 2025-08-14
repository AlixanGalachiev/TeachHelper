# tests/test_user_repository.py
import pytest
from app.models.model_user import Role
from app.repositories.repo_user import UserRepository

@pytest.mark.asyncio
async def test_create_and_get_user(session):
		repo = UserRepository(session)

		# Создаём пользователя
		user = await repo.create(
			email="test@example.com",
			password="123456",
			full_name="Test User",
			role=Role.student
		)

		await session.commit()

		assert user.id is not None
		assert user.email == "test@example.com"

		# Проверяем поиск по email
		found = await repo.get_by_email("test@example.com")
		assert found is not None
		assert found.email == "test@example.com"

		await repo.delete(user.id)
		await session.commit()
  

