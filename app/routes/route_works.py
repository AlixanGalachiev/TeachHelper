import uuid
from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.models.model_tasks import StatusWork
from app.models.model_users import Users
from app.schemas.schema_comment import *
from app.services.service_comments import ServiceComments
from app.services.service_files import ServiceFiles
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


@router.post("/{id}/comments")
async def create_comment(
    data: CommentCreate,
    session: AsyncSession = Depends(get_async_session),
    user: Users = Depends(get_current_user)
):
    service = ServiceComments(session)
    return await service.create(data, user)

@router.put("/{id}/comments/{comment_id}")
async def update_comment(
    id: uuid.UUID,
    comment_id: uuid.UUID,
    data: CommentUpdate,
    session: AsyncSession = Depends(get_async_session),
    user: Users = Depends(get_current_user)
):
    service = ServiceComments(session)
    return await service.update(comment_id, data, user)

@router.delete("/{id}/comments/{comment_id}")
async def delete_comment(
    comment_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    user: Users = Depends(get_current_user)
):
    service = ServiceComments(session)
    return await service.delete(comment_id, user)


@router.post("/{id}/comments/{comment_id}/files")
async def create_file(
    id: uuid.UUID,
    comment_id: uuid.UUID,
    files: list[UploadFile],
    session: AsyncSession = Depends(get_async_session),
    user: Users = Depends(get_current_user)
):
    service = ServiceFiles(session)
    return service.create(
        comment_id,
        'comments',
        files,
        user
    )


@router.delete("/{id}/comments/{comment_id}/files/{file_id}")
async def delete_file(
    id: uuid.UUID,
    comment_id: uuid.UUID,
    file_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    user: Users = Depends(get_current_user)
):
    service = ServiceFiles(session)
    return service.delete(file_id, 'comments', user)
