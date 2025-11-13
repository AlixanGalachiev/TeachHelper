import enum
import uuid
import asyncio

from fastapi import HTTPException
from sqlalchemy import Column, Table, event
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UUID, ForeignKey, Integer, String

from app.config.boto import get_boto_client
from app.config.config_app import settings
from app.utils.logger import logger
from app.models.base import Base

class FileEntity(enum.Enum):
    answer = "answer"
    comment = "comment"
    work = "work"
    task = "task"
    exercise = "exercise"

comments_files = Table(
    "comments_files",
    Base.metadata,
    Column[uuid.UUID]("id", UUID(as_uuid=True), default=uuid.uuid4),
    Column[uuid.UUID]("file_id", ForeignKey("files.id", ondelete="CASCADE"), nullable=False),
    Column[uuid.UUID]("comment_id", ForeignKey("comments.id", ondelete="CASCADE"), nullable=False)
)

answers_files = Table(
    "answers_files",
    Base.metadata,
    Column("id", UUID(as_uuid=True), default=uuid.uuid4),
    Column("file_id", ForeignKey("files.id", ondelete="CASCADE"), nullable=False),
    Column("answer_id", ForeignKey("answers.id", ondelete="CASCADE"), nullable=False)
)

tasks_files = Table(
    "tasks_files",
    Base.metadata,
    Column("id", UUID(as_uuid=True), default=uuid.uuid4),
    Column("file_id", ForeignKey("files.id", ondelete="CASCADE"), nullable=False),
    Column("task_id", ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
)

exercises_files = Table(
    "exercises_files",
    Base.metadata,
    Column("id", UUID(as_uuid=True), default=uuid.uuid4),
    Column("file_id", ForeignKey("files.id", ondelete="CASCADE"), nullable=False),
    Column("exercise_id", ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False)
)



class Files(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    original_size: Mapped[int] = mapped_column(Integer, nullable=False)
    original_mime: Mapped[str] = mapped_column(String, nullable=False)


@event.listens_for(Files, 'before_delete')
def delete_file_from_minio(mapper, connection, target):
    """
    Удаление файла из MinIO при удалении записи из БД.
    Используется синхронная функция, так как SQLAlchemy events не поддерживают async.
    Для async операций используется asyncio.run().
    """
    try:
        
        async def _delete_file():
            file_key = f"{target.id}/{target.filename}"
            async with get_boto_client() as s3:
                await s3.delete_object(Bucket=settings.MINIO_BUCKET, Key=file_key)
        
        # Запускаем async функцию в синхронном контексте
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Если event loop уже запущен, создаем задачу
                asyncio.create_task(_delete_file())
            else:
                loop.run_until_complete(_delete_file())
        except RuntimeError:
            # Если нет event loop, создаем новый
            asyncio.run(_delete_file())
    except Exception as exc:
        logger.error(f"Failed to delete file from MinIO: {target.id}/{target.filename}. Error: {exc}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
