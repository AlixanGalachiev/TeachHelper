from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.schemas.schema_classroom import ClassroomCreate, ClassroomRead, ClassroomAddStudent
from app.repositories.repo_classroom import ClassroomRepository

router = APIRouter(prefix="/classrooms", tags=["Classrooms"])


@router.post("", response_model=ClassroomRead, status_code=status.HTTP_201_CREATED)
async def create_classroom(payload: ClassroomCreate, db: AsyncSession = Depends(get_async_session)):
    repo = ClassroomRepository(db)
    classroom = await repo.create(name=payload.name, teacher_id=payload.teacher_id)
    await db.commit()
    await db.refresh(classroom)
    return classroom


@router.get("/{classroom_id}", response_model=ClassroomRead)
async def get_classroom(classroom_id: int, db: AsyncSession = Depends(get_async_session)):
    repo = ClassroomRepository(db)
    classroom = await repo.get(classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    return classroom


@router.get("", response_model=list[ClassroomRead])
async def list_classrooms(teacher_id: int | None = None, limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_async_session)):
    repo = ClassroomRepository(db)
    items = await repo.list(teacher_id=teacher_id, limit=limit, offset=offset)
    return list(items)


@router.post("/{classroom_id}/students", status_code=204)
async def add_student(classroom_id: int, payload: ClassroomAddStudent, db: AsyncSession = Depends(get_async_session)):
    repo = ClassroomRepository(db)
    cls = await repo.get(classroom_id)
    if not cls:
        raise HTTPException(status_code=404, detail="Classroom not found")
    await repo.add_student(classroom_id=classroom_id, user_id=payload.user_id)
    await db.commit()
    return None


@router.delete("/{classroom_id}", status_code=204)
async def delete_classroom(classroom_id: int, db: AsyncSession = Depends(get_async_session)):
    repo = ClassroomRepository(db)
    await repo.remove(classroom_id)
    await db.commit()
    return None
