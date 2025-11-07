import uuid

from pydantic import BaseModel


class FileSchema(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    filename: str
    bucket: str
    original_size: int
    original_mime: str

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": uuid.UUID("ecefeaf2-d21d-426f-b415-9ff1dfb4da0a"),
                "user_id": uuid.UUID("9ca843a9-7163-472c-b67a-8b730567f272"),
                "filename": "simple.txt",
                "bucket": "comment",
                "original_size": "12",
                "original_mime": ".txt",
            }
        }
    }