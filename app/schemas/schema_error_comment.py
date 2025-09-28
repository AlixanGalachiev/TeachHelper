import uuid
from pydantic import BaseModel

from app.models.model_error_comment import ErrorType

class ErrorCommentCreate(BaseModel):
	work_id: uuid.UUID
	type: ErrorType

	description: str   | None = None

