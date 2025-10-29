import uuid

from fastapi import HTTPException, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import  joinedload, selectinload, Load

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.repo_task import RepoTasks
from app.schemas.schema_tasks import ExerciseCriterionRead, ExerciseRead, TaskCreate, TaskRead, TaskSchema, TasksFilters, TasksReadEasy, TasksPatch
from app.models.model_tasks import ExerciseCriterions, Exercises, Tasks
from app.models.model_users import RoleUser, Users
from app.utils.logger import logger

class ServiceTasks:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, teacher: Users, data: TaskCreate) -> TaskSchema:
        try:
            if teacher.role is RoleUser.student:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User don't have permission to delete this task")

            task = Tasks(
                name=data.name,
                description=data.description,
                subject_id=data.subject_id,
                teacher_id=teacher.id,
            )

            for ex_data in data.exercises:
                exercise = Exercises(
                    name=ex_data.name,
                    description=ex_data.description,
                    order_index=ex_data.order_index,
                )

                for cr_data in ex_data.criterions:
                    criterion = ExerciseCriterions(
                        name=cr_data.name,
                        score=cr_data.score,
                    )
                    exercise.criterions.append(criterion)
                task.exercises.append(exercise)

            self.session.add(task)
            await self.session.commit()
            return JSONResponse(
                content=TaskSchema.model_validate(task).model_dump(mode='json'),
                status_code=status.HTTP_201_CREATED
            )

        except HTTPException as exc:
            raise

        except Exception as exc:
            logger.exception(exc)
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Internal Server Error")


    async def get_all(self, teacher: Users, filters: TasksFilters) -> list[TasksReadEasy]:
        try:
            if teacher.role is RoleUser.student:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User don't have permission to delete this task")

            query = (
                select(
                    Tasks.id,
                    Tasks.name,
                    Tasks.updated_at
                )
                .where(Tasks.teacher_id == teacher.id)
            )
            if filters.name is not None:
               query = query.where(Tasks.name.ilike(f'%{filters.name}%'))
            
            response = await self.session.execute(query)
            tasks =  response.mappings().all()
            return [TasksReadEasy.model_validate(task) for task in tasks]
    
        except HTTPException as exc:
            raise

        except Exception as exc:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Internal Server Error")


    async def get(self, id: uuid.UUID, teacher: Users) -> TaskSchema:
        try:
            if teacher.role is RoleUser.student:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User don't have permission to delete this task")
            repo = RepoTasks(self.session)
            task = await repo.get(id)

            if not task: 
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

            return TaskSchema.model_validate(task)

        except HTTPException as exc:
            raise

        except Exception as exc:
            logger.exception(exc)
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Internal Server Error")


    async def update(self, id: uuid.UUID, update_data: TaskSchema, teacher: Users) -> TaskSchema:
        try:
            if teacher.role is RoleUser.student:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User don't have permission to delete this task")

            task_db = await self.session.get(Tasks, id)
            if not task_db: 
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
            
            exercises_orm = []
            for exercise_data in update_data.exercises:
                criterions_orm = [
                    ExerciseCriterions(**criterion.model_dump())
                    for criterion in exercise_data.criterions
                ]

                exercise_dict = exercise_data.model_dump(exclude={"criterions"})
                exercise_orm = Exercises(**exercise_dict)
                exercise_orm.criterions = criterions_orm
                exercises_orm.append(exercise_orm)

            task_dict = update_data.model_dump(exclude={"exercises"})
            task_orm = Tasks(**task_dict)
            task_orm.exercises = exercises_orm

            await self.session.merge(task_orm)
            await self.session.commit()
            repo = RepoTasks(self.session)
            return TaskSchema.model_validate(await repo.get(id)).model_dump(mode="json")

        except HTTPException as exc:
            raise

        except Exception as exc:
            logger.exception(exc)
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)


    async def delete(self, id: uuid.UUID, teacher: Users) -> JSONResponse:
        try:
            if teacher.role is RoleUser.student:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User don't have permission to delete this task")

            task = await self.session.get(Tasks, id)
            if task is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

            if task.teacher_id != teacher.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User don't have permission to delete this task")

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

