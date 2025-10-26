

import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.models.model_users import Users
from app.schemas.schema_tasks import TaskCreate, TaskRead, TasksFilters, TasksPatch
from app.services.service_tasks import ServiceTasks
from app.utils.oAuth import get_current_user


router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=TaskRead)
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



@router.patch("/{id}")
async def patch(
    id: uuid.UUID,
    update_data: TasksPatch,
    session: AsyncSession = Depends(get_async_session),
    teacher: Users = Depends(get_current_user)
):
    service = ServiceTasks(session)
    return await service.patch(id, update_data, teacher)


@router.delete("/{id}")
async def delete(
    id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    teacher: Users = Depends(get_current_user)
):
    service = ServiceTasks(session)
    return await service.delete(id, teacher)



# @router.post("/{id}")
# async def task_add(
#     session: AsyncSession = Depends(get_async_session),
#     teacher: Users = Depends(get_current_user)
# ):
#     service = ServiceTasks(session)
#     return service.task_add()


# @router.get("/{id}")
# async def get(
#     session: AsyncSession = Depends(get_async_session),
#     teacher: Users = Depends(get_current_user)
# ):
#     service = ServiceTasks(session)
#     return service.get()
