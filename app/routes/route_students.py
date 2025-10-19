import os
from fastapi import APIRouter, Depends

from app.config.config_app import settings
from app.db import get_async_session
from app.models.model_users import Users
from app.services.teacher.service_students import ServiceStudents
from app.utils.oAuth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter('/students', tags=["Teacher","Students"])


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
    return service.get_all(current_user)

    
@router.get("/{id}")
async def get(
    session: AsyncSession = Depends(get_async_session),
    current_user: Users = Depends(get_current_user)
    ):

@router.post("/{id}")
async def post(
    session: AsyncSession = Depends(get_async_session),
    current_user: Users = Depends(get_current_user)
    ):

@router.update("/{id}")
async def update(
    session: AsyncSession = Depends(get_async_session),
    current_user: Users = Depends(get_current_user)
    ):

@router.delete("/{id}")
async def delete(
    session: AsyncSession = Depends(get_async_session),
    current_user: Users = Depends(get_current_user)
    ):
