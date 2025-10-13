from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.schemas.schema_auth import UserCreate, UserRead, UserUpdate
from app.repositories.repo_user import UserRepo
from app.models.model_user import RoleUser
from app.utils.oAuth import get_current_user


router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserRead)
async def get_user(current_user=Depends(get_current_user)):
	return current_user

@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, db: AsyncSession = Depends(get_async_session), current_user=Depends(get_current_user)):
    repo = UserRepo(db)
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("", response_model=list[UserRead])
async def list_users(limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_async_session), current_user=Depends(get_current_user)):
    repo = UserRepo(db)
    users = await repo.list(limit=limit, offset=offset)
    return list(users)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(user_id: int, payload: UserUpdate, db: AsyncSession = Depends(get_async_session), current_user=Depends(get_current_user)):
    repo = UserRepo(db)
    data = payload.dict(exclude_unset=True)
    if "role" in data:
        data["role"] = RoleUser(data["role"])
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await repo.update(user_id, **data)
    await db.commit()
    updated = await repo.get(user_id)
    return updated


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_async_session), current_user=Depends(get_current_user)):
    repo = UserRepo(db)
    await repo.delete(user_id)
    await db.commit()
    return None
