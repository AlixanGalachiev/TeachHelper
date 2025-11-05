import uuid
from pydantic import BaseModel

from app.schemas.schema_files import FileSchema


class CommentCreate(BaseModel):
    id: uuid.UUID
    answer_id: uuid.UUID
    type_id: uuid.UUID

class CommentRead(CommentCreate):
    id: uuid.UUID
    answer_id: uuid.UUID
    type_id: uuid.UUID
    description: str
    files: list[FileSchema]|None = None

# сначала удаляем файл потом получаем комментарий
class CommentUpdate(BaseModel):
    type_id: uuid.UUID
    description: str
