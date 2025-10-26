import uuid
from pydantic import BaseModel

class SubjectRead(BaseModel):
    id: uuid.UUID
    name: str
    
    model_config = {
        "from_atributes": True,
    }
