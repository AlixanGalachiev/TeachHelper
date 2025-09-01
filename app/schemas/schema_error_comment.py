from pydantic import BaseModel

class ErrorCommentCreate(BaseModel):
	work_id: uuid.UUID
	type: ErrorComment

	description: str   | None = None

