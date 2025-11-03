from datetime import datetime
from fastapi import HTTPException, status
import uuid
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.model_tasks import ACriterions, Answers, Exercises, StatusWork, Tasks, Works
from app.models.model_users import  RoleUser, Users
from app.schemas.schema_tasks import SchemaTask
from app.schemas.schema_work import WorkAllFilters
from app.utils.logger import logger
from pydantic import BaseModel

from app.repositories.repo_work import RepoWorks


class ACriterionBase(BaseModel):
    answer_id:             uuid.UUID
    exercise_criterion_id: uuid.UUID

class ACriterionRead(BaseModel):
    id:        uuid.UUID
    completed: bool

    model_config = {
        "from_attributes": True,
    }


class ACriterionUpdate(BaseModel):
    id:        uuid.UUID|None = None
    completed: bool|None = None



class AnswerBase(BaseModel):
    work_id:     uuid.UUID
    exercise_id: uuid.UUID
    file_url:    str|None = None

class AnswerRead(AnswerBase):
    id:          uuid.UUID
    criterions:  list[ACriterionRead]

    model_config = {
        "from_attributes": True,
    }

class AnswerUpdate(AnswerBase):
    id:          uuid.UUID|None = None
    criterions: list[ACriterionUpdate]


class WorkBase(BaseModel):
    task_id:     uuid.UUID
    student_id:  uuid.UUID
    finish_date: datetime|None = None
    status:      StatusWork

class WorkRead(WorkBase):
    id: uuid.UUID
    answers: list[AnswerRead]

    model_config = {
        "from_attributes": True,
    }

class WorkUpdate(WorkRead):
    answers: list[AnswerUpdate]

class WorkEasyRead(BaseModel):
    id: uuid.UUID
    task_name: str
    student_name: str
    score: int
    max_score: int
    percent: int
    status_work: StatusWork

    model_config = {
        "from_attributes": True,
    }



class ServiceWork:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def get(self, id: uuid.UUID):
        try:
            stmt = (
                select(Works)
                .where(Works.id == id)
                .options(
                    selectinload(Works.answers)
                    .selectinload(Answers.criterions)
                )
            )
            response = await self.session.execute(stmt)
            work_db = response.scalars().first()
            
            if work_db is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work not exists")
     
            stmt = (
                select(Tasks)
                .where(Tasks.id == work_db.task_id)
                .options(
                    selectinload(Tasks.exercises)
                    .selectinload(Exercises.criterions)
                )
            )
            response = await self.session.execute(stmt)
            task_db = response.scalars().first()

            return JSONResponse(
                content={
                    "task": SchemaTask.model_validate(task_db).model_dump(mode="json"),
                    "work": WorkRead.model_validate(work_db).model_dump(mode="json")
                },
                status_code=status.HTTP_200_OK
            )

        except HTTPException as exc:
            raise

        except Exception as exc:
            logger.exception(exc)
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Internal Server Error")


    async def get_all(self, filters: dict, user: Users) -> list[WorkEasyRead]:
        try:
            filters = WorkAllFilters.model_validate(filters)
            repo = RepoWorks(self.session)
            rows = await repo.get_all(filters, user)

            work_list = []
            for row in rows:
                # Распаковка результата и расчет процента
                score = row.score if row.score is not None else 0
                max_score = row.max_score if row.max_score is not None and row.max_score > 0 else 1 # Избегаем деления на ноль

                percent = round((score / max_score) * 100)
                
                work_list.append(
                    WorkEasyRead(
                        id=row.id,
                        student_name=row.student_name,
                        task_name=row.task_name,
                        score=score,
                        max_score=row.max_score,
                        percent=percent,
                        status_work=row.status_work
                    )
                )
            
            return work_list
            
        except HTTPException as exc:
            raise
        
        except Exception as exc:
            logger.exception(exc)
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Internal Server Error")


    async def update(self, work_id: uuid.UUID, work_data: WorkUpdate, user: Users):
        try:
            if user.role is RoleUser.teacher:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User don't have permission to delete this work")

            if work_id != work_data.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Work data id must match with work_id")
            print(work_id)
            work_db = await self.session.get(Works, work_id)
            if work_db is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work not exists")
            
            answers = []
            for answer in work_data.answers:
                criterions_orm = [
                    ACriterions(**criterion.model_dump())
                    for criterion in answer.criterions
                ]
                
                answer_orm = Answers(**answer.model_dump(exclude={"criterions"}))
                answer_orm.criterions = criterions_orm
                answers.append(answer_orm)

            work = Works(**work_data.model_dump(exclude={"answers"}))
            work.answers = answers
            await self.session.merge(work)
            await self.session.commit()
            
            stmt = (
                select(Works)
                .where(Works.id==work_id)
                .options(
                    selectinload(Works.answers)
                    .selectinload(Answers.criterions)
                )
            )
            response = await self.session.execute(stmt)
            rows = response.scalars().first()
            return WorkRead.model_validate(rows).model_dump(mode="json")

        except HTTPException as exc:
            raise

        except Exception as exc:
            logger.exception(exc)
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Internal Server Error")


    # async def delete(self, work_id: uuid.UUID, user: Users):
    #     try:
    #         if user.role is RoleUser.student:
    #             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User don't have permission to delete this task")

    #         work_db = await self.session.get(Works, work_id)
    #         if work_db in None:
    #             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work not exists")

    #         await self.session.delete(work_db)
    #         await self.session.commit()

    #         return JSONResponse(
    #             content={"status": "ok"},
    #             status_code=status.HTTP_200_OK
    #         )
           
            
    #     except HTTPException as exc:
    #         raise
        
    #     except Exception as exc:
    #         logger.exception(exc)
    #         await self.session.rollback()
    #         raise HTTPException(status_code=500, detail="Internal Server Error")
