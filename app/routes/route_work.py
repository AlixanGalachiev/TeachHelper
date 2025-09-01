from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from app.db import get_async_session
from app.repositories.repo_user import UserRepo
from app.schemas.schema_user import UserCreate, UserRead
from app.utils.oAuth import create_access_token
from app.utils.password import verify_password
from app.utils.logger import logger
from datetime import datetime, timezone

import os

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
			raise HTTPException(status_code=403, "Wrong user role")
			
		classroom_stmt = select(Classroom.id).where(
			Classroom.name.in_(classroom_names)
		)
		response = await db.session.execute(classroom_stmt)
		classroom_ids = response.scalars().all()

		user_ids_stmt = select(classroom_students.c.student_id).where(
			classroom_students.c.classroom_id.in_(classroom_ids)
		)
		response = await db.session.execute(classroom_stmt)
		classroom_students_ids = response.scalars().all()
		external_filters.student_ids.append(*classroom_students_ids)

		filters = [
			"teacher_id": current_user.id,
			"limit": limit,
			"offset": offset,
			"statuses": work_statuses
		]

		if len(external_filters.student_ids) != 0:
			filters['students_ids'] = external_filters.student_ids

		repo = WorkRepo(db)

		response = await repo.teacher_get_works(**filters)

		return [WorkRow(**row) for row in response]

	except:
		session.rollback()
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
		session.rollback()
		await db.rollback()
		raise HTTPException(status_code=500, detail="Internal Server Error")
	

@router.patch("/{work_id}/verify")
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
		filtered_data = work_data.dict(exclude_none=True)

		for field, value in data.items():
			setattr(work, field, value)

		await db.commit()
		await db.refresh(work)
	except Exception as e:
		logger.error(f"Ошибка при завершении проверки: {e}", exc_info=True)
		await db.rollback()
		raise HTTPException(status_code=500, detail="Internal Server Error")


	return {"work_data": work, "error_comments": work.error_comments}


@router.patch("/{work_id}/finish_verification")
async def finish_work_verification(
	work_id: uuid.UUID,
	db: AsyncSession = Depends(get_async_session),
	current_user = Depends(get_current_user)
):
	try:
		work = await db.get(Work, work_id)
		if not work:
			raise HTTPException(status_code=404, detail="Work not found")

		work.status = WorkStatus.checked
		await db.commit()
		return True

	except Exception as e:
		logger.error(f"Ошибка при завершении проверки: {e}", exc_info=True)
		await db.rollback()
		raise HTTPException(status_code=500, detail="Internal Server Error")


@router.patch("/{work_id}/start")
async def start_task_completion(
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
		

@router.patch("/{work_id}/update")
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
	
	
@router.patch("/{work_id}/finish")
async def finish_work_completion(
	work_id: uuid.UUID,
	db: AsyncSession = Depends(get_async_session),
	current_user = Depends(get_current_user)
):
	try:
		work = await db.get(Work, work_id)
		if not work:
			raise HTTPException(status_code=404, detail="Work not found")

		work.status = WorkStatus.on_checking
		work.finish_date = datetime.now(timezone.utc)

		await db.commit()
		return True

	except:
		session.rollback()
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
		row = await self.repo.detail(work_id)
		if not row:
			raise HTTPException(status_code=404, detail="Work not found")
		return WorkDetailRead(**row)

	except:
		session.rollback()
		await db.rollback()
		raise HTTPException(status_code=500, detail="Internal Server Error")

