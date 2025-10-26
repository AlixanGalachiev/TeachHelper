import uuid

from fastapi import HTTPException, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.schema_tasks import TaskCreate, TaskRead, TasksFilters, TasksReadEasy, TasksPatch
from app.models.model_tasks import Tasks
from app.models.model_users import Users
from app.utils.logger import logger

class ServiceTasks:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, teacher: Users, data: TaskCreate):
        stmt = (
            select(Tasks)
            .where(Tasks.teacher_id == teacher.id)
            .where(Tasks.title == data.title)
            .where(Tasks.subject_id == data.subject_id)
        )
        task_db = await self.session.execute(stmt)
        if task_db.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Task with this name is already exists for choosed subject"
        )

        task = Tasks(**data.model_dump(), teacher_id=teacher.id)
        self.session.add(task)
        await self.session.flush()
        await self.session.commit()
        return TaskRead.model_validate(task)

        

    async def get_all(self, teacher: Users, filters: TasksFilters):
        stmt = select(
            Tasks.id,
            Tasks.title,
            Tasks.updated_at,
            ).where(Tasks.teacher_id == teacher.id)

        if filters.title:
            stmt = stmt.where(Tasks.title.ilike(f"%{filters.title}%"))
            
        if filters.subject_id:
            stmt = stmt.where(Tasks.subject_id == filters.subject_id)

        result = await self.session.execute(stmt)
        tasks = result.mappings().all()
        return [TasksReadEasy.model_validate(task) for task in tasks]


    # async def task_add(self, ):
    #     pass

    # Нужно определиться что должно вывестись
    # async def get(self, id: uuid.UUID, teacher: Users):
    #     pass

    async def patch(self, id: uuid.UUID, update_data: TasksPatch, teacher: Users):
        try:
            task = await self.session.get(Tasks, id)
            if not task: 
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

            if task.teacher_id != teacher.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to delete this task"
                )

            update_data = update_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(task, key, value)

            await self.session.commit()
            return JSONResponse(
                content={"status": "ok"},
                status_code=status.HTTP_200_OK
            )

        except HTTPException as exc:
            raise

        except Exception as exc:
            logger.exception(exc)
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)


    async def delete(self, id: uuid.UUID, teacher: Users):
        try:
            task = await self.session.get(Tasks, id)
            if task.teacher_id != teacher.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to delete this task"
                )

            await self.session.delete(task)
            await self.session.commit()
            return JSONResponse(
                content={"status": "ok"},
                status_code=status.HTTP_200_OK
            )

        except HTTPException as exc:
            raise

        except Exception as exc:
            logger.exception(exc)
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)

