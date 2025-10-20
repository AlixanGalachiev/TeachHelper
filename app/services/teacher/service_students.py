import uuid
from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.model_users import Users
from app.repositories.repo_classrooms import RepoClassroom
from app.repositories.teacher.repo_students import RepoStudents

from app.utils.logger import logger


class ServiceStudents:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_all(self, teacher: Users):
       students_repo = RepoStudents(self.session)
       students = await students_repo.get_all(teacher)

       classrooms_repo = RepoClassroom(self.session)
       classrooms = await classrooms_repo.get_teacher_classrooms

       return {
           "students": students,
           "classrooms": classrooms
       }
       

    async def get_performans_data(self, student_id: uuid.UUID, teacher: Users):
        repo = RepoStudents(self.session)
        if not await repo.exists(teacher.id, student_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Студент не найден"
            )
        results = await repo.get_performans_data(student_id)

        for row in results["works_data"]:
            student = results["agg_data"][row.user_id]
            student.setdefault("works", []).append({
                "submission_id": row.submission_id,
                "status": row.status,
                "total_score": row.total_score,
                "task_title": row.task_title,
                "max_score": row.max_score
            })

        return results["agg_data"]

    async def move_to_class(
        self,
        student_id: uuid.UUID,
        class_id: uuid.UUID,
        teacher: Users
    ):
        try:
            repo = RepoStudents(self.session)
            if not await repo.exists(teacher.id, student_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Студент не найден"
                )
            if await repo.user_exists_in_class(teacher.id, student_id, class_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Студент уже находится в этом классе"
                )
            await repo.move_to_class(teacher.id, student_id, class_id)
            await self.session.commit()
            return JSONResponse(content={"status": "ok"}, status_code=status.HTTP_200_OK)
        except HTTPException:
            raise
        except Exception as exc:
            logger.exception("Ошибка при перемещении ученика в класс")
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def remove_from_class(
        self,
        student_id: uuid.UUID,
        class_id: uuid.UUID,
        teacher: Users
    ):
        repo = RepoStudents(self.session)
        try:
            if not await repo.exists(teacher.id, student_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Студент не найден"
                )
            if not await repo.user_exists_in_class(teacher.id, student_id, class_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Студент не состоит в этом классе"
                )
            await repo.remove_from_class(teacher.id, student_id, class_id)
            await self.session.commit()
            return JSONResponse(content={"status": "ok"}, status_code=status.HTTP_200_OK)
        except HTTPException:
            raise
        except Exception as exc:
            logger.exception("Ошибка при удалении ученика из класса")
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def delete(
        self,
        student_id: uuid.UUID,
        teacher: Users
    ):
        repo = RepoStudents(self.session)
        try:
            if not await repo.exists(teacher.id, student_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Студент не найден"
                )
            await repo.delete(teacher_id=teacher.id, student_id=student_id)
            await self.session.commit()
            return JSONResponse(content={"status": "ok"}, status_code=status.HTTP_200_OK)
        except HTTPException:
            raise
        except Exception as exc:
            logger.exception("Ошибка при удалении ученика")
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
