from typing import Sequence, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.hash import bcrypt

from app.models import *

from app.schemas import SubscriptionCreate, SubscriptionRead, SubscriptionUpdate
from app.utils.password import get_password_hash
from datetime import datetime
import uuid





class SubscriptionRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: SubscriptionCreate) -> SubscriptionRead:
        new_sub = Subscription(
            id=uuid.uuid4(),
            type=data.type,
            price=data.price,
            description=data.description
        )
        self.session.add(new_sub)
        await self.session.commit()
        await self.session.refresh(new_sub)
        return SubscriptionRead.model_validate(new_sub)

    async def get(self, id: uuid.UUID) -> SubscriptionRead | None:
        query = select(Subscription).where(Subscription.id == id)
        result = await self.session.execute(query)
        sub = result.scalar_one_or_none()
        if not sub:
            raise HTTPException(404, detail="This subscription doesn't exists")

        return SubscriptionRead.model_validate(sub)

    async def update(self, data: SubscriptionUpdate) -> SubscriptionRead | None:
        query = (
            update(Subscription)
            .where(Subscription.id == data.id)
            .values(
                price=data.price if data.price is not None else Subscription.price,
                description=data.description if data.description is not None else Subscription.description,
                type=data.type if data.type is not None else Subscription.type,
            )
            .returning(Subscription)
        )
        result = await self.session.execute(query)
        updated = result.scalar_one_or_none()
        if not updated:
            raise HTTPException(404, detail="This subscription doesn't exists")

        await self.session.commit()
        return SubscriptionRead.model_validate(updated)

    async def delete(self, id: uuid.UUID) -> bool:
        query = delete(Subscription).where(Subscription.id == id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0


