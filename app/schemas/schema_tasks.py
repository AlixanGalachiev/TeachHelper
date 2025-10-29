from pydantic import BaseModel
import uuid
from datetime import datetime

class ExerciseCriterionCreate(BaseModel):
    name:  str
    score: int

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "name": "Посчитал до 10",
                "score": 1,
            }
        }
    }

class ExerciseCriterionRead(BaseModel):
    id:    uuid.UUID
    name:  str
    score: int
    model_config = {
        "from_attributes": True
    }

class ExerciseCreate(BaseModel):
    name:        str
    description: str
    order_index: int

    criterions: list[ExerciseCriterionCreate]

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "name": "Посчитай 10",
                "description": "Очень важно",
                "order_index": 1,  
                "criterions": [
                    {
                        "name": "Посчитал до 10",
                        "score": 1,
                    }
                ]
            }
        }
    }


class ExerciseRead(ExerciseCreate):
    id:          uuid.UUID
    name:        str
    description: str
    order_index: int
    criterions: list[ExerciseCriterionRead]
    
    model_config = {
        "from_attributes": True,
        "by_alias": True,
        
    }


class TaskCreate(BaseModel):
    subject_id:  uuid.UUID
    name:        str
    description: str
    deadline:    datetime|None = None
    
    exercises: list[ExerciseCreate]

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "subject_id": "b1697c3a-5486-4bea-8aed-4e2552be92f3",
                "name": "Задача по математике",
                "description": "Решить 10 уравнений",

                "exercises": [{
                        "name": "Посчитай 10",
                        "description": "Очень важно",
                        "order_index": 1,
                        "criterions": [
                            {
                                "name": "Посчитал до 10",
                                "score": 1,
                            }
                        ]
                    }
                ]
            }
        }
    }

class ExerciseCriterions(BaseModel):
    id:          uuid.UUID|None = None
    name:        str
    score:       int
    exercise_id: uuid.UUID
    updated_at:  datetime|None = None
    created_at:  datetime|None = None

    model_config = {
        "from_attributes": True,
    }

class ExerciseSchema(BaseModel):
    id:          uuid.UUID|None = None
    name:        str        
    description: str            
    order_index: int            
    task_id:     uuid.UUID
    updated_at:  datetime|None = None
    created_at:  datetime|None = None
    criterions:  list[ExerciseCriterions]

    model_config = {
        "from_attributes": True,
    }      

class TaskSchema(BaseModel):
    id:          uuid.UUID
    name:        str
    description: str
    deadline:   datetime|None = None

    subject_id: uuid.UUID
    teacher_id: uuid.UUID
    updated_at: datetime|None = None
    created_at: datetime|None = None
    exercises:   list[ExerciseSchema]

    model_config = {
        "from_attributes": True,
    }
    

class TaskRead(BaseModel):
    id: uuid.UUID
    name:        str
    description: str
    deadline:    datetime|None = None
    exercises: list[ExerciseRead]
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
                "updated_at": "2023-10-26T12:00:00",
                "created_at": "2023-10-26T12:00:00",
                
                "exercises": [{
                        "id": "",
                        "name": "Посчитай 10",
                        "description": "Очень важно",
                        "order_index": 1,
                        "criterions": [
                            {
                                "id": "",
                                "name": "Посчитал до 10",
                                "score": 1,
                            }
                        ]
                    }
                ]
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

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Математика",
                "subject_id": "b1697c3a-5486-4bea-8aed-4e2552be92f3"
            }
        }
    }