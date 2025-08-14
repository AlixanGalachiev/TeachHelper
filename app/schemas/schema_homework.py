from pydantic import BaseModel
from typing import Optional, List
from .schema_error import ErrorItemCreate, ErrorItemRead


class HomeworkCreate(BaseModel):
    student_id: int
    classroom_id: Optional[int] = None
    file_path: Optional[str] = None
    recognized_text: Optional[str] = None


class HomeworkUpdate(BaseModel):
    status: Optional[str] = None
    recognized_text: Optional[str] = None


class HomeworkRead(BaseModel):
    id: int
    student_id: int
    classroom_id: Optional[int] = None
    file_path: Optional[str] = None
    recognized_text: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


class HomeworkWithErrors(HomeworkRead):
    errors: List[ErrorItemRead] = []
