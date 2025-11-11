import uuid
from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_async_session
from app.models.model_files import FileEntity
from app.models.model_users import Users
from app.schemas.schema_work import AnswerRead, AnswerUpdate
from app.services.service_answers import ServiceAnswers
from app.services.service_files import ServiceFiles
from app.utils.oAuth import get_current_user

 
teacher_router = APIRouter(prefix="teacher/works/{work_id}/answers", tags=["Answers", "student"])

@teacher_router.patch("/{answer_id}")
async def teacher_update(
    work_id: uuid.UUID,
    answer_id: uuid.UUID,
    general_comment: str,
    session: AsyncSession = Depends(get_async_session),
    user: Users = Depends(get_current_user)

):
    service = ServiceAnswers
    return await service.update_comment(
        work_id,
        answer_id,
        general_comment,
        user
    )



student_router = APIRouter(prefix="student/works/{work_id}/answers", tags=["Answers", "student"])

@student_router.post("/{answer_id}/files")
async def add_files(
    work_id: uuid.UUID,
    answer_id: uuid.UUID,
    files: list[UploadFile],
    session: AsyncSession = Depends(get_async_session),
    user: Users = Depends(get_current_user)
):
    service = ServiceFiles(session)
    return await service.create(entity=FileEntity.answer, entity_id=answer_id, files=files, user=user)


@student_router.post("/{answer_id}/files{id}")
async def update(
    work_id: uuid.UUID,
    answer_id: uuid.UUID,
    id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    user: Users = Depends(get_current_user)
):

    service = ServiceFiles(session)
    return await service.delete(file_id=id, user=user)


