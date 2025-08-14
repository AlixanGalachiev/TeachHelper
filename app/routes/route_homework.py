from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.schemas.schema_homework import HomeworkCreate, HomeworkRead, HomeworkUpdate, HomeworkWithErrors
from app.schemas.schema_error import ErrorItemCreate, ErrorItemRead
from app.repositories.repo_homework import HomeworkRepository
from app.repositories.repo_error import ErrorRepository

router = APIRouter(prefix="/homeworks", tags=["Homeworks"])


@router.post("", response_model=HomeworkRead, status_code=status.HTTP_201_CREATED)
async def create_homework(payload: HomeworkCreate, db: AsyncSession = Depends(get_async_session)):
    repo = HomeworkRepository(db)
    hw = await repo.create(
        student_id=payload.student_id,
        classroom_id=payload.classroom_id,
        file_path=payload.file_path,
        recognized_text=payload.recognized_text,
    )
    await db.commit()
    await db.refresh(hw)
    return hw


@router.get("/{homework_id}", response_model=HomeworkRead)
async def get_homework(homework_id: int, db: AsyncSession = Depends(get_async_session)):
    repo = HomeworkRepository(db)
    hw = await repo.get(homework_id)
    if not hw:
        raise HTTPException(status_code=404, detail="Homework not found")
    return hw


@router.get("", response_model=list[HomeworkRead])
async def list_homeworks(student_id: int | None = None, classroom_id: int | None = None, limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_async_session)):
    repo = HomeworkRepository(db)
    items = await repo.list(student_id=student_id, classroom_id=classroom_id, limit=limit, offset=offset)
    return list(items)


@router.patch("/{homework_id}", response_model=HomeworkRead)
async def update_homework(homework_id: int, payload: HomeworkUpdate, db: AsyncSession = Depends(get_async_session)):
    repo = HomeworkRepository(db)
    hw = await repo.update(homework_id, **payload.dict(exclude_unset=True))
    if not hw:
        raise HTTPException(status_code=404, detail="Homework not found")
    await db.commit()
    return hw


@router.delete("/{homework_id}", status_code=204)
async def delete_homework(homework_id: int, db: AsyncSession = Depends(get_async_session)):
    repo = HomeworkRepository(db)
    await repo.delete(homework_id)
    await db.commit()
    return None


# ---- Ошибки по домашке ----

@router.get("/{homework_id}/errors", response_model=list[ErrorItemRead])
async def list_errors(homework_id: int, db: AsyncSession = Depends(get_async_session)):
    repo = ErrorRepository(db)
    items = await repo.list_for_homework(homework_id)
    return list(items)


@router.post("/{homework_id}/errors", status_code=204)
async def add_errors(homework_id: int, payload: list[ErrorItemCreate], db: AsyncSession = Depends(get_async_session)):
    hw_repo = HomeworkRepository(db)
    if not await hw_repo.get(homework_id):
        raise HTTPException(status_code=404, detail="Homework not found")
    await hw_repo.add_errors(homework_id, [e.dict() for e in payload])
    await db.commit()
    return None
