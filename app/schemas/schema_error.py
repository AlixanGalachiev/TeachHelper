from pydantic import BaseModel


class ErrorItemCreate(BaseModel):
    kind: str
    message: str
    start_pos: int
    end_pos: int


class ErrorItemRead(ErrorItemCreate):
    id: int
    homework_id: int

    class Config:
        from_attributes = True
