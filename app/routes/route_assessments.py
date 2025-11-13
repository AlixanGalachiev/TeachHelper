import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_async_session
from app.exceptions.responses import Success
from app.models.model_files import FileEntity
from app.models.model_tasks import Tasks
from app.models.model_users import Users
from app.models.model_works import Answers, Assessments, Works
from app.services.service_assessments import ServiceAssessments
from app.services.service_comments import ServiceComments
from app.services.service_files import ServiceFiles
from app.utils.oAuth import get_current_user


router = APIRouter(prefix="/worsk/{work_id}/answers/{answer_id}/assessments", tags=["Answers"])

@router.put("/{id}")
async def update(
    work_id: uuid.UUID,
    answer_id: uuid.UUID,
    id: uuid.UUID,
    points: int,
    session: AsyncSession = Depends(get_async_session),
    user: Users = Depends(get_current_user)
):
    service = ServiceAssessments(session)
    return await service.update(work_id, answer_id, id, points, user,)