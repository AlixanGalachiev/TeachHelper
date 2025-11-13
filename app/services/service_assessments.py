import uuid

from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.exceptions.responses import Success
from app.models.model_tasks import Tasks
from app.models.model_users import Users
from app.models.model_works import Answers, Assessments, Works
from app.services.service_base import ServiceBase
from app.utils.logger import logger


class ServiceAssessments(ServiceBase):

    async def update(
        self,
        work_id: uuid.UUID,
        answer_id: uuid.UUID,
        id: uuid.UUID,
        points: int,
        user: Users,
    ):
        try:
            stmt = (
                select(Assessments)
                .join(Answers, Assessments.answer_id == Answers.id)
                .join(Works, Answers.work_id == Works.id)
                .join(Tasks, Works.task_id == Tasks.id)
                .where(
                    Assessments.id == id,
                    Answers.id == answer_id,
                    Works.id == work_id,
                    Tasks.teacher_id == user.id
                )
                .options(
                    selectinload(Assessments.answer)
                    .selectinload(Answers.work)
                    .selectinload(Works.task),
                    selectinload(Assessments.criterion)
                )
            )
            response  = await self.session.execute(stmt)
            assessment_db = response.scalars().first()

            if assessment_db is None:
                raise HTTPException(status_code=404, detail="Assessment not found")  # защищаемся от некорректных идентификаторов

            if points > assessment_db.criterion.score:
                raise HTTPException(400, "Too many points")

            assessment_db.points = points
            await self.session.commit()

            return Success()
            
        except HTTPException:
            await self.session.rollback()
            raise
        
        except Exception as exc:
            logger.exception(exc)
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Internal Server Error")
