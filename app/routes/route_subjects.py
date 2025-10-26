import uuid
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.models.model_users import Users
from app.services.service_subjects import ServiceSubjects
from app.utils.oAuth import get_current_user


router = APIRouter(prefix="/subjects", tags="Subjects")

@router.post("/")
async def create(
    name: str,
    session: AsyncSession = Depends(get_async_session),
    user: Users = Depends(get_current_user)
):
    service = ServiceSubjects(session)
    return service.create(name=name, user=user) 
    
@router.get("/")
async def get_all(
    session: AsyncSession = Depends(get_async_session),
    user: Users = Depends(get_current_user)
):
    service = ServiceSubjects(session)
    return service.get_all()
    
@router.patch("/{id}")
async def patch(
    id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    user: Users = Depends(get_current_user)
):
    service = ServiceSubjects(session)
    return service.patch(id=id, user=user) 
    
@router.delete("/{id}")
async def delete(
    session: AsyncSession = Depends(get_async_session),
    user: Users = Depends(get_current_user)
):
    service = ServiceSubjects(session)
    return service.delete(id=id, user=user) 
    