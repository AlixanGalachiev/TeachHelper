import uuid
from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.model_users import Users
from app.repositories.repo_classrooms import RepoClassroom
from app.repositories.repo_user import RepoUser
from app.repositories.teacher.repo_students import RepoStudents

from app.schemas.schema_auth import UserRole
from app.exceptions.exceptions import ErrorRolePermissionDenied
from app.utils.logger import logger




class ServiceStudents:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_all(self, user: Users):
        if user.role != UserRole.teacher:
            raise ErrorRolePermissionDenied(UserRole.teacher)

        students_repo = RepoStudents(self.session)
        students = await students_repo.get_all(user)

        classrooms_repo = RepoClassroom(self.session)
        classrooms = await classrooms_repo.get_teacher_classrooms(user.id)

        return {
           "students": students,
           "classrooms": classrooms
        }


    async def get_performans_data(self, student_id: uuid.UUID, user: Users):
        if user.role != UserRole.teacher:
            raise ErrorRolePermissionDenied(UserRole.teacher)

        repo = RepoStudents(self.session)
        if not await repo.exists(user.id, student_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Студент не найден"
            )
        return await repo.get_performans_data(student_id)
        

    async def move_to_class(
        self,
        student_id: uuid.UUID,
        classroom_id: uuid.UUID,
        user: Users
    ):
        try:
            if user.role != UserRole.teacher:
                raise ErrorRolePermissionDenied(UserRole.teacher)
            
            repo = RepoStudents(self.session)
            if not await repo.exists(user.id, student_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Студент не найден"
                )
            if await repo.user_exists_in_class(user.id, student_id, classroom_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Студент уже находится в этом классе"
                )
            await repo.move_to_class(user.id, student_id, classroom_id)
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
        classroom_id: uuid.UUID,
        user: Users
    ):
        repo = RepoStudents(self.session)
        try:
            if user.role != UserRole.teacher:
                raise ErrorRolePermissionDenied(UserRole.teacher)
            
            if not await repo.exists(user.id, student_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Студент не найден"
                )
            if not await repo.user_exists_in_class(user.id, student_id, classroom_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Студент не состоит в этом классе"
                )
            await repo.remove_from_class(user.id, student_id, )
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
        user: Users
    ):
        try:
            if user.role != UserRole.teacher:
                raise ErrorRolePermissionDenied(UserRole.teacher)
            
            repo = RepoStudents(self.session)
            if not await repo.exists(user.id, student_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Студент не найден"
                )
            await repo.delete(teacher_id=user.id, student_id=student_id)
            await self.session.commit()
            return JSONResponse(content={"status": "ok"}, status_code=status.HTTP_200_OK)
        except HTTPException:
            raise
        except Exception as exc:
            logger.exception("Ошибка при удалении ученика")
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def add_teacher(self, teacher_id: uuid.UUID, student: Users):
        if student.role != UserRole.student:
            raise ErrorRolePermissionDenied(UserRole.student)

        repo_user = RepoUser(self.session)
        if await repo_user.get(teacher_id) is  None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Teacher is not exists")

        repo = RepoStudents(self.session)
        await repo.add_teacher(teacher_id, student.id)
        await self.session.commit()
        return JSONResponse(
            {"status": "ok"},
            status.HTTP_201_CREATED
        )
        
        
        
            
            