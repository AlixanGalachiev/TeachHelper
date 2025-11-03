

import uuid
from pydantic import BaseModel

from app.models.model_tasks import StatusWork


class WorkAllFilters(BaseModel):
    subject_id: uuid.UUID|None = None
    student_id: uuid.UUID|None = None
    classroom_id: uuid.UUID|None = None
    status_work: StatusWork|None = None
