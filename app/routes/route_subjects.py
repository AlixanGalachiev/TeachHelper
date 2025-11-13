import uuid
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.models.model_users import Users
from app.services.service_subjects import ServiceSubjects
from app.services.service_comment_types import ServiceCommentTypes, SchemaCommentTypesBase
from app.utils.oAuth import get_current_user


router = APIRouter(prefix="/subjects", tags=["Subjects"])

@router.post("")
async def create(
    name: str,
    session: AsyncSession = Depends(get_async_session),
    user: Users = Depends(get_current_user)
):
    service = ServiceSubjects(session)
    return await service.create(name=name, user=user)

@router.get("")
async def get_all(
    session: AsyncSession = Depends(get_async_session),
    user: Users = Depends(get_current_user)
):
    service = ServiceSubjects(session)
    return await service.get_all()
    
@router.patch("/{id}")
async def patch(
    id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    user: Users = Depends(get_current_user)
):
    service = ServiceSubjects(session)
    return await service.patch(id=id, user=user) 
    
@router.delete("/{id}")
async def delete(
    id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    user: Users = Depends(get_current_user)
):
    service = ServiceSubjects(session)
    return await service.delete(id=id, user=user) 


# comment_types: создать для предмета
@router.post("/{subject_id}/comment_types")
async def create_comment_type(
    subject_id: uuid.UUID,
    data: SchemaCommentTypesBase,
    session: AsyncSession = Depends(get_async_session),
    user: Users = Depends(get_current_user)
):
    service = ServiceCommentTypes(session)
    return await service.create(id=subject_id, data=data, user=user)


# comment_types: получить все по предмету
@router.get("/{subject_id}/comment_types")
async def get_comment_types(
    subject_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    user: Users = Depends(get_current_user)
):
    service = ServiceCommentTypes(session)
    return await service.get_all(subject_id=subject_id, user=user)


# comment_types: обновить по id типа
@router.put("/{subject_id}/comment_types/{id}")
async def update_comment_type(
    id: uuid.UUID,
    data: SchemaCommentTypesBase,
    session: AsyncSession = Depends(get_async_session),
    user: Users = Depends(get_current_user)
):
    service = ServiceCommentTypes(session)
    return await service.update(id=id, data=data, user=user)


# comment_types: удалить по id типа
@router.delete("/{subject_id}/comment_types/{id}")
async def delete_comment_type(
    id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    user: Users = Depends(get_current_user)
):
    service = ServiceCommentTypes(session)
    return await service.delete(id=id, user=user) 

