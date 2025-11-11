import uuid
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.responses import *
from app.config.boto import get_boto_client
from app.config.config_app import settings
from app.models.model_comments import Comments
from app.models.model_users import RoleUser, Users
from app.schemas.schema_comment import CommentCreate, CommentUpdate
from app.utils.logger import logger
from app.services.service_base import ServiceBase

class ServiceComments(ServiceBase):

    async def create(self, data: CommentCreate, user: Users):
        try:
            if user.role is RoleUser.student:
                raise ErrorRolePermissionDenied(RoleUser.teacher, user.role) 

            comment = Comments(**data)
            self.session.add(comment)
            await self.session.commit()
            return JSONResponse(
                content={"status": "ok"},
                status_code=201
            )
        except HTTPException:
            raise
        
        except Exception as exc:
            logger.exception(exc)
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Internal Server Error")

    async def update(self, comment_id: uuid.UUID, update_data: CommentUpdate, user: Users):
        try:
            if user.role is RoleUser.Student:
                raise ErrorRolePermissionDenied(RoleUser.teacher, RoleUser.student)

            comment_db = await self.session.get(Comments, comment_id)
            if comment_db is None:
                raise ErrorNotExists(comment_id, Comments)

            for key, value in update_data.items():
                if hasattr(comment_db, key):
                    setattr(comment_db, key, value)

            await self.session.commit()
            return JSONResponse(
                content={"status": "ok"},
                status_code=200
            )

        except HTTPException:
            await self.session.rollback()
            raise
        
        except Exception as exc:
            logger.exception(exc)
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Internal Server Error")


    async def delete(self, comment_id: uuid.UUID, user: Users):
        try:
            if user.role is RoleUser.Student:
                raise ErrorRolePermissionDenied(RoleUser.teacher, RoleUser.student)

            comment_db = await self.session.get(
                Comments,
                comment_id,
                options=(
                    joinedload(Comments.files)
                )
            )

            if comment_db is None:
                raise ErrorNotExists(comment_id, Comments)

            bucket = settings.MINIO_BUCKET
            async with get_boto_client() as s3:
                for file in comment_db.files:
                    file_key = f"{file.id}/{file.filename}"
                    await s3.delete_object(
                        Bucket=bucket,
                        Key=file_key
                    )

            await self.session.delete(comment_db)
            await self.session.commit()
            return JSONResponse({"status": "ok"}, 200)


        except HTTPException:
            await self.session.rollback()
            raise
        
        except Exception as exc:
            logger.exception(exc)
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Internal Server Error")


