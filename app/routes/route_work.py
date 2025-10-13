import uuid
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from app.db import get_async_session, get_sync_session
from app.models.model_classroom import Classroom
from app.models.model_error_comment import ErrorComment
from app.models.model_work import Work, WorkStatus
from app.repositories.repo_work import WorkRepo
from app.schemas.schema_error_comment import ErrorCommentCreate
from app.schemas.schema_auth import UserRole
from app.schemas.schema_work import UpdateWorkByTeacher, WorkDetailRead, WorksGetByTeacher
from app.services.HTRService.trOCR_recognition import handle_images
from app.utils.logger import logger
from datetime import datetime, timezone

import os
import cv2

from app.utils.oAuth import get_current_user

router = APIRouter(prefix="/works", tags=["works"])

UPLOAD_DIR = "public/filesWork"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/teacher")
async def get_works_by_teacher(
	external_filters: WorksGetByTeacher,
	db: AsyncSession = Depends(get_async_session),
	current_user = Depends(get_current_user),
	limit      : int = 10,
	offset     : int = 0,
):
	try:
		if current_user.role != UserRole.teacher:
			raise HTTPException(status_code=403, detail= "Wrong user role")
			
		classroom_stmt = select(Classroom.id).where(
			Classroom.name.in_(classroom_names)
		)
		response = await db.db.execute(classroom_stmt)
		classroom_ids = response.scalars().all()

		user_ids_stmt = select(classroom_students.c.student_id).where(
			classroom_students.c.classroom_id.in_(classroom_ids)
		)
		response = await db.db.execute(classroom_stmt)
		classroom_students_ids = response.scalars().all()
		external_filters.student_ids.append(*classroom_students_ids)

		filters = {
			"teacher_id": current_user.id,
			"limit": limit,
			"offset": offset,
			"statuses": work_statuses
		}

		if len(external_filters.student_ids) != 0:
			filters['students_ids'] = external_filters.student_ids

		repo = WorkRepo(db)

		response = await repo.teacher_get_works(**filters)

		return [WorkRow(**row) for row in response]

	except:
		db.rollback()
		await db.rollback()
		raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/student")
async def get_works_by_teacher(
	db: AsyncSession = Depends(get_async_session),
	current_user = Depends(get_current_user),
	limit      : int = 10,
	offset     : int = 0,
):
	try:
		repo = WorkRepo(db)
		rows = await repo.student_get_works(current_user.id, limit, offset)
		return [WorkRow(**row) for row in response]
	except:
		db.rollback()
		await db.rollback()
		raise HTTPException(status_code=500, detail="Internal Server Error")
	

@router.patch("/{work_id}/verification/finish")
async def verify_work(
	work_id: uuid.UUID,
	work_data: UpdateWorkByTeacher,
	comments: list[ErrorCommentCreate],
	db: AsyncSession = Depends(get_async_session),
	current_user = Depends(get_current_user),
):
	try:
		work = await db.get(Work, work_id)
		if not work:
			raise HTTPException(status_code=404, detail="Work not found")

		if len(comments) > 0:
			new_comments = [
				ErrorComment(
					work_id=item.work_id,
					type=item.type,
					description=item.description
				)
				for item in comments
			]

			db.add_all(new_comments)
		filtered_data = work_data.model_dump(exclude_none=True)

		for field, value in filtered_data.items():
			setattr(work, field, value)
		work.status = WorkStatus.checked

		await db.commit()
		await db.refresh(work)
	except Exception as e:
		logger.error(f"Ошибка при завершении проверки: {e}", exc_info=True)
		await db.rollback()
		raise HTTPException(status_code=500, detail="Internal Server Error")


	return {"work_data": work, "error_comments": work.error_comments}


@router.patch("/{work_id}/execution/start")
async def start_task_execution(
	work_id: uuid.UUID,
	db:AsyncSession = Depends(get_async_session),
	current_user = Depends(get_current_user)
):
	try:
		work = await db.get(Work, work_id)
		if not work:
			raise HTTPException(status_code=404, detail="Work not found")

		work.status = WorkStatus.in_work
		await db.commit()
		return True
	except:
		logger.error(f"Ошибка при завершении проверки: {e}", exc_info=True)
		await db.rollback()
		raise HTTPException(status_code=500, detail="Internal Server Error")
		

@router.patch("/{work_id}/execution/update")
async def update_work_by_student(
	work_id: uuid.UUID,
	files: list[UploadFile] = File(...),
	db: AsyncSession = Depends(get_async_session),
	current_user = Depends(get_current_user)
):
	try:
		work = await db.get(Work, work_id)
		if not work:
			raise HTTPException(status_code=404, detail="Work not found")

		saved_files = []

		for file in files:
			# уникальное имя файла
			ext = os.path.splitext(file.filename)[1]
			filename = f"{uuid.uuid4()}{ext}"
			filepath = os.path.join(UPLOAD_DIR, filename)

			# сохраняем файл
			with open(filepath, "wb") as buffer:
				shutil.copyfileobj(file.file, buffer)

			# генерируем URL для хранения в БД
			file_url = f"/filesWork/{filename}"
			saved_files.append(file_url)

			# допустим, у Work есть поле "files" (JSON или Array)
			if work.files is None:
				work.files = []
			work.files.append(file_url)

		await db.commit()
		await db.refresh(work)

		return {"work_id": work_id, "files": saved_files}

	except:
		logger.error(f"Ошибка при завершении проверки: {e}", exc_info=True)
		await db.rollback()
		raise HTTPException(status_code=500, detail="Internal Server Error")
	
	
@router.patch("/{work_id}/execution/finish")
async def finish_work_completion(
	work_id: uuid.UUID,
	db: AsyncSession = Depends(get_async_session),
	background_tasks: BackgroundTasks = None,
	current_user = Depends(get_current_user)
):
	try:
		work = await db.get(Work, work_id)
		if not work:
			raise HTTPException(status_code=404, detail="Work not found")

		work.status = WorkStatus.on_checking
		work.finish_date = datetime.now(timezone.utc)

		work = await db.get(Work, work_id)
		background_tasks.add_task(verificate_work_by_ai, work_id)

		await db.commit()
		return True

	except:
		db.rollback()
		await db.rollback()
		raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/{work_id}")
async def detail(
	work_id: uuid.UUID,
	db: AsyncSession = Depends(get_async_session),
	current_user = Depends(get_current_user)
):
	try:
		repo = WorkRepo(db)
		row = await repo.detail(work_id)
		if not row:
			raise HTTPException(status_code=404, detail="Work not found")
		return WorkDetailRead(**row)

	except:
		db.rollback()
		await db.rollback()
		raise HTTPException(status_code=500, detail="Internal Server Error")


def verificate_work_by_ai(work_id: uuid.UUID):
	with get_sync_session() as session:
		work = session.get(Work, work_id)
		handle_results = handle_images(work.images)

		for img_path, image in handle_results:
			cv2.imwrite(f"{os.getenv('WORK_ERROR_IMAGES')}/{os.path.basename(img_path)}", image)

		work.verifed_by_ai = True
		session.commit()
