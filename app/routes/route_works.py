import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.models.model_tasks import StatusWork
from app.models.model_users import Users
from app.schemas.schema_work import WorkAllFilters
from app.services.service_work import ServiceWork, WorkEasyRead, WorkUpdate
from app.utils.oAuth import get_current_user


router = APIRouter(prefix="/works", tags=["Works"])
    
@router.get("", response_model=list[WorkEasyRead])
async def get_all(
    subject_id: uuid.UUID|None = None,
    student_id: uuid.UUID|None = None,
    classroom_id: uuid.UUID|None = None,
    status_work: StatusWork|None = None,
    session: AsyncSession = Depends(get_async_session),
    user: Users = Depends(get_current_user)
):
    service = ServiceWork(session)
    return await service.get_all(
        {
            "subject_id": subject_id,
            "student_id": student_id,
            "classroom_id": classroom_id,
            "status_work": status_work,
        },
        user
    )


@router.get("/{id}")
async def get(
    id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    user: Users = Depends(get_current_user)
):
    service = ServiceWork(session)
    return await service.get(id)


@router.put("/{id}")
async def update(
    id: uuid.UUID,
    data: WorkUpdate,
    session: AsyncSession = Depends(get_async_session),
    user: Users = Depends(get_current_user)
):
    service = ServiceWork(session)
    return await service.update(id, data, user)

    
# @router.delete("/{id}")
# async def delete(
#     id: uuid.UUID,
#     session: AsyncSession = Depends(get_async_session),
#     user: Users = Depends(get_current_user)
# ):
#     service = ServiceWork(session)
#     return await service.delete(id, user)
