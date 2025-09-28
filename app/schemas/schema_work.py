import uuid

from datetime import datetime
from pydantic import BaseModel
from app.models import ErrorComment, WorkStatus

class WorkDetailRead(BaseModel):
    work_id:     uuid.UUID
    taskname:    str
    description: str
    first_name:  str
    middle_name: str
    last_name:   str
    points:      int
    max_point:   int
    work_files:  list[str] 
    task_files:  list[str] 



class UpdateWorkByTeacher(BaseModel):
	points:           int | None = None
	teacher_comment:  str | None = None


class WorkEdit(BaseModel):
	files:   str|None = None


class CreateWork(BaseModel):
	files:  str
	task_id:    uuid.UUID
	student_id: uuid.UUID

	status: WorkStatus    | None = None
	points:      int      | None = None
	finish_date: datetime | None = None


class WorksFiltersTeacher(BaseModel):
	class_name : str | None        = None
	student_id : uuid.UUID | None  = None
	status     : WorkStatus | None = None
	limit      : int = 10
	offset     : int = 0


class WorksGetByTeacher(BaseModel):
	student_ids:     list[uuid.UUID] | None = None
	classroom_names: list[str]  | None = None
	work_statuses:     list[WorkStatus] = [WorkStatus.on_checking, WorkStatus.checked]


class WorkRow(BaseModel):
	work_id:     uuid.UUID
	first_name:  str
	middle_name: str
	last_name:   str
	max_point:   int
	points:      int
	status:      WorkStatus
	task_name:   str




