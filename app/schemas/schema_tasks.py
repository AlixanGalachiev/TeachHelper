from pydantic import BaseModel, field_validator
import uuid
from datetime import timezone, datetime

class TaskCreate(BaseModel):
    subject_id: uuid.UUID
    name: str
    description: str
    deadline: datetime|None = None
    max_score: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "subject_id": "b1697c3a-5486-4bea-8aed-4e2552be92f3",
                "name": "Задача по математике",
                "description": "Решить 10 уравнений",
                "max_score": 100
            }
        }
    }

class TaskRead(TaskCreate):
    id: uuid.UUID
    updated_at: datetime
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "subject_id": "b1697c3a-5486-4bea-8aed-4e2552be92f3",
                "name": "Задача по математике",
                "description": "Решить 10 уравнений",
                "deadline": "2025-12-31T23:59:59",
                "max_score": 100,
                "updated_at": "2023-10-26T12:00:00",
                "created_at": "2023-10-26T12:00:00"
            }
        }
    }


class TasksReadEasy(BaseModel):
    id: uuid.UUID
    name: str
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "name": "Задача по математике",
                "updated_at": "2023-10-26T12:00:00"
            }
        }
    }

class TasksPatch(BaseModel):
    name: str|None = None
    description: str|None = None
    deadline: str|None = None
    max_score: int|None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Обновленное название задачи",
                "description": "Обновленное описание",
                "deadline": "2025-12-31T23:59:59",
                "max_score": 150
            }
        }
    }


class TasksFilters(BaseModel):
    name: str|None = None
    subject_id: uuid.UUID|None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Математика",
                "subject_id": "b1697c3a-5486-4bea-8aed-4e2552be92f3"
            }
        }
    }