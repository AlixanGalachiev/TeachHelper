import uuid
from pydantic import BaseModel

from app.models.model_tasks import StatusSubmission


class SchemaStudentPerfomansWorks(BaseModel):
        submission_id: uuid.UUID
        status: StatusSubmission
        total_score: int
        task_title: str
        max_score: int

class SchemaStudentPerformans(BaseModel):
    student_id: uuid.UUID
    student_name: str
    verificated_works_count: int
    avg_score: int
    works: list[SchemaStudentPerfomansWorks]
