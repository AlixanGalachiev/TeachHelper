from typing import Sequence, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.hash import bcrypt

from app.models.model_user import User, Role
from app.schemas.schema_user import UserCreate
from app.utils.auth import get_password_hash


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_data: UserCreate) -> User:
        user = User(
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            role=user_data.role,
        )
        self.session.add(user)
        await self.session.flush()
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
        await self.session.execute(update(User).where(User.id == user_id).values(**fields))
        await self.session.flush()
        return await self.get(user_id)

    async def delete(self, user_id: int) -> bool:
        await self.session.execute(delete(User).where(User.id == user_id))
        return True
