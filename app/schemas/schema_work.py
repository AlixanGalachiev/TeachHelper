

import uuid
from pydantic import BaseModel

from app.models.model_works import StatusWork


class WorkAllFilters(BaseModel):
    subject_id: uuid.UUID|None = None
    students_ids: list[uuid.UUID]|None = None
    classrooms_ids: list[uuid.UUID]|None = None
    status_work: StatusWork|None = None