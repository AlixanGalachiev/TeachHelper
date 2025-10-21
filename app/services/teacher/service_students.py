import uuid
from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.model_users import Users
from app.repositories.repo_classrooms import RepoClassroom
from app.repositories.repo_user import RepoUser
from app.repositories.teacher.repo_students import RepoStudents

from app.schemas.schema_auth import UserRole
from app.utils.logger import logger


class ServiceStudents:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_all(self, teacher: Users):
        students_repo = RepoStudents(self.session)
        students = await students_repo.get_all(teacher)

        classrooms_repo = RepoClassroom(self.session)
        classrooms_response = await classrooms_repo.get_teacher_classrooms(teacher.id)

        classrooms = {}
        for classroom in classrooms_response:
            cid = classroom["classroom_id"]
            if cid not in classrooms:
                classrooms[cid] = {
                    "id": cid,
                    "name": classroom["classroom_name"],
                    "students": []
                }
            if classroom["student_id"] != None: 
                classrooms[cid]["students"].append({
                    "id": classroom["student_id"],
                    "name": classroom["student_name"]
                })


        return {
           "students": students,
           "classrooms": list(classrooms.values())
        }


    async def get_performans_data(self, student_id: uuid.UUID, teacher: Users):
        repo = RepoStudents(self.session)
        if not await repo.exists(teacher.id, student_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Студент не найден"
            )
        results = await repo.get_performans_data(student_id)
        
        students = {}
        for s in results["agg_data"]:
            student_id = s["student_id"]
            students[student_id] = dict(s)
            students[student_id]["works"] = []


        for row in results["works_data"]:
            student_id = row["student_id"]
            if student_id in students:
                students[student_id]["works"].append({
                    "submission_id": row["submission_id"],
                    "status": row["status"],
                    "total_score": row["total_score"],
                    "task_title": row["task_title"],
                    "max_score": row["max_score"]
                })

        return list(students.values())

    async def move_to_class(
        self,
        student_id: uuid.UUID,
        classroom_id: uuid.UUID,
        teacher: Users
    ):
        try:
            repo = RepoStudents(self.session)
            if not await repo.exists(teacher.id, student_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Студент не найден"
                )
            if await repo.user_exists_in_class(teacher.id, student_id, classroom_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Студент уже находится в этом классе"
                )
            await repo.move_to_class(teacher.id, student_id, classroom_id)
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
        teacher: Users
    ):
        repo = RepoStudents(self.session)
        try:
            if not await repo.exists(teacher.id, student_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Студент не найден"
                )
            if not await repo.user_exists_in_class(teacher.id, student_id, classroom_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Студент не состоит в этом классе"
                )
            await repo.remove_from_class(teacher.id, student_id, )
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

    async def add_teacher(self, teacher_id: uuid.UUID, student: Users):
        if student.role != UserRole.student:
            raise HTTPException(status.HTTP_423_LOCKED, "User is not a student")

        repo_user = RepoUser(self.session)
        if repo_user.get(teacher_id) is  None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Teacher is not exists")

        repo = RepoStudents(self.session)
        await repo.add_teacher(teacher_id, student.id)
        await self.session.commit()
        return JSONResponse(
            {"status": "ok"},
            status.HTTP_201_CREATED
        )
        
        
        
            
            