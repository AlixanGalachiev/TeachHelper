import uuid

from sqlalchemy import event
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UUID, ForeignKey, Integer, String
from fastapi import HTTPException

from app.config.boto import get_boto_client
from app.utils.logger import logger
from app.models.base import Base

class Files(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    bucket: Mapped[str] = mapped_column(String, nullable=False)
    original_size: Mapped[int] = mapped_column(Integer, nullable=False)
    original_mime: Mapped[str] = mapped_column(String, nullable=False)

@event.listens_for(Files, 'before_delete')
async def delete_file_from_minio(mapper, connection, target):
    s3 = await get_boto_client()
    try:
        await s3.delete_object(Bucket=target.bucket, Key=f"{target.id}/{target.filename}")
    except Exception as exc:
        logger.exception(exc)
        raise HTTPException(status_code=500, detail="Internal Server Error")
