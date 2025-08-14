from pydantic import BaseModel
from typing import Optional, List


class ClassroomBase(BaseModel):
    name: str


class ClassroomCreate(ClassroomBase):
    teacher_id: int


class ClassroomRead(ClassroomBase):
    id: int
    teacher_id: int

    class Config:
        from_attributes = True


class ClassroomAddStudent(BaseModel):
    user_id: int


class ClassroomWithStudents(ClassroomRead):
    student_ids: List[int]
