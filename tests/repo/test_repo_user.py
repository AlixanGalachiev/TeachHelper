# tests/test_repo_usersitory.py
import pytest
from app.models.model_user import RoleUser
from app.repositories.repo_user import UserRepo
from app.schemas.schema_user import UserCreate
from app.utils.password import verify_password

@pytest.mark.asyncio
async def test_repo_user(session):
		repo_user = UserRepo(session)
		# Создаём пользователя
		user = await repo_user.create(
			UserCreate(
				email="test@example.com",
				password="123456",
				first_name = "Ali", 
				middle_name = "Mara", 
				last_name = "Gall",
				role=RoleUser.student
			)
		)

		await session.commit()

		assert user.id is not None
		assert user.email == "test@example.com"


		user_by_email = await repo_user.get_by_email("test@example.com")
		assert user_by_email is not None
		assert user_by_email.email == "test@example.com"

		user_updated = await repo_user.update(user.id, first_name = "ali_new", password="111111")
		assert user.id == user_updated.id
		assert user_updated.first_name == "ali_new"
		assert verify_password("111111", user_updated.password_hash)

		await session.commit()

		await repo_user.delete(user.id)
		await session.commit()

		response = await repo_user.get(user.id)
		response == None
