import os
import uuid
from fastapi import APIRouter, Depends

from app.config.config_app import settings
from app.db import get_async_session
from app.models.model_users import Users
from app.schemas.schema_students import SchemaStudentPerformans
from app.services.teacher.service_students import ServiceStudents
from app.utils.oAuth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix='/teacher', tags=["Teacher"])


@router.get("/invite_link")
async def get_link(
    current_user: Users = Depends(get_current_user)
    ):
    return {"link": f"{settings.FRONT_URL}/t/{current_user.id}"}
    

@router.get("/")
async def get_all(
    session: AsyncSession = Depends(get_async_session),
    current_user: Users = Depends(get_current_user)
    ):
    service = ServiceStudents(session)
    return await service.get_all(current_user)


@router.get("/{id}")
async def get(
    id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: Users = Depends(get_current_user)
    ):
    service = ServiceStudents(session)
    return await service.get_performans_data(student_id=id, teacher=current_user)



@router.patch("/{id}/move_to_class")
async def update(
    id: uuid.UUID,
    classroom_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: Users = Depends(get_current_user)
    ):
    service = ServiceStudents(session)
    return await service.move_to_class(student_id=id, classroom_id=classroom_id, teacher=current_user)


@router.patch("/{id}/remove_from_class")
async def update(
    id: uuid.UUID,
    classroom_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: Users = Depends(get_current_user)
    ):
    service = ServiceStudents(session)
    return await service.remove_from_class(student_id=id, classroom_id=classroom_id, teacher=current_user)





@router.delete("/{id}")
async def delete(
    id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: Users = Depends(get_current_user)
    ):
    service = ServiceStudents(session)
    return await service.delete(student_id=id, teacher=current_user)

router2 = APIRouter(tags=['Student'])

@router2.post("/teacher")
async def add(
    teacher_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    student: Users = Depends(get_current_user)):
    service = ServiceStudents(session)
    return await service.add_teacher(teacher_id, student)