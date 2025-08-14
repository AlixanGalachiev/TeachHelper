from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.schemas.schema_user import UserCreate, UserRead, UserUpdate
from app.repositories.repo_user import UserRepository
from app.models.model_user import Role

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_async_session)):
    repo = UserRepository(db)
    existing = await repo.get_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await repo.create(
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
        role=Role(payload.role),
    )
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, db: AsyncSession = Depends(get_async_session)):
    repo = UserRepository(db)
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("", response_model=list[UserRead])
async def list_users(limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_async_session)):
    repo = UserRepository(db)
    users = await repo.list(limit=limit, offset=offset)
    return list(users)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(user_id: int, payload: UserUpdate, db: AsyncSession = Depends(get_async_session)):
    repo = UserRepository(db)
    data = payload.dict(exclude_unset=True)
    if "role" in data:
        data["role"] = Role(data["role"])
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await repo.update(user_id, **data)
    await db.commit()
    updated = await repo.get(user_id)
    return updated


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_async_session)):
    repo = UserRepository(db)
    await repo.delete(user_id)
    await db.commit()
    return None
