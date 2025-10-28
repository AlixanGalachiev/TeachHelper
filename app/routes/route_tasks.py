import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.models.model_users import Users
from app.schemas.schema_tasks import ExerciseCreate, ExerciseCriterionCreate, TaskCreate, TaskRead, TasksFilters, TasksPatch
from app.services.service_tasks import ServiceTasks
from app.utils.oAuth import get_current_user


router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/")
# @router.post("/", response_model=TaskRead)
async def create(
    data: TaskCreate,
    session: AsyncSession = Depends(get_async_session),
    teacher: Users = Depends(get_current_user)
):
    service = ServiceTasks(session)
    return await service.create(teacher, data)

@router.get("/")
async def get_all(
    filters: TasksFilters = Depends(),
    session: AsyncSession = Depends(get_async_session),
    teacher: Users = Depends(get_current_user)
):
    service = ServiceTasks(session)
    return await service.get_all(teacher, filters)


@router.get("/{id}")
async def get(
    id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    teacher: Users = Depends(get_current_user)
):
    service = ServiceTasks(session)
    return await service.get(id, teacher)


@router.put("/{id}")
async def update(
    id: uuid.UUID,
    update_data: TaskRead,
    session: AsyncSession = Depends(get_async_session),
    teacher: Users = Depends(get_current_user)
):
    service = ServiceTasks(session)
    return await service.update(id, update_data, teacher)


@router.delete("/{id}")
async def delete(
    id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    teacher: Users = Depends(get_current_user)
):
    service = ServiceTasks(session)
    return await service.delete(id, teacher)

