import uuid
from pydantic import BaseModel

class SchemaClassroomsFilter(BaseModel):
    classroom_name: str|None = None

class SchemaClassroomBase(BaseModel):
    classroom_id: uuid.UUID

class SchemaClassroom(BaseModel):
    id: uuid.UUID
    teacher_id: uuid.UUID
    name: str
    model_config = {
        'from_attributes': True
    }