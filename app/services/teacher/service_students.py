import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.model_users import Users
from app.repositories.repo_classrooms import RepoClassroom
from app.repositories.teacher.repo_students import RepoStudents

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
       
    class SchemaStudentPerfomansWorks(BaseModel):
        submission_id: uuid.UUID
        status: SubmissionStatus
        total_score: int
        task_title: str
        max_score: int

    class SchemaStudentPerformans(BaseModel):
        student_id: uuid.UUID
        student_name: str
        verificated_works_count: int
        avg_score: int
        works: list[SchemaStudentPerfomansWorks]

    async def get_performans_data(self, student_id: uuid.UUID):
        repo = RepoStudents(self.session)
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

        return {
            "data": results["agg_data"]
        }
        

    # async def post(self,):

    # async def update(self,):

    # async def delete(self,):
