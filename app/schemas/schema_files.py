import uuid

from pydantic import BaseModel


class FileSchema(BaseModel):
    id: uuid.UUID
    original_size: int
    original_mime: int
    url: str
    thumbnail_url: str|None = None
