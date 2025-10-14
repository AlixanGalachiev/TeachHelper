from typing import Sequence, Optional
from sqlalchemy import select, update, delete, exists
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.hash import bcrypt

from app.models.model_user import RoleUser, User
from app.schemas.schema_auth import UserRegister
from app.utils.password import get_password_hash
from datetime import datetime


class UserRepo:
    def __init__(self, session: AsyncSession):
        self.session = session
  
    async def email_exists(self, email):
        stmt = select(User).where(User.email == email)
        response = await self.session.execute(stmt)
        result = response.scalar_one_or_none()
        print(result)
        return result is not None
        

    async def create(self, user: User) -> User:
        self.session.add(user)
        return user

    async def get(self, user_id: int) -> Optional[User]:
        res = await self.session.execute(select(User).where(User.id == user_id))
        return res.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        res = await self.session.execute(select(User).where(User.email == email))
        return res.scalar_one_or_none()

    async def list(self, limit: int = 100, offset: int = 0) -> Sequence[User]:
        res = await self.session.execute(select(User).offset(offset).limit(limit))
        return res.scalars().all()

    async def update(self, user_id: int, **fields) -> Optional[User]:
        if "password" in fields:
            fields["password_hash"] = bcrypt.hash(fields.pop("password"))
        result = await self.session.execute(update(User).where(User.id == user_id).values(**fields).returning(User))
        return result.scalar_one_or_none()

    async def delete(self, user_id: int) -> bool:
        await self.session.execute(delete(User).where(User.id == user_id))
        return True


