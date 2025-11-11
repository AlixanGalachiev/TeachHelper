
import enum
import uuid

from fastapi import HTTPException, UploadFile, logger
from fastapi.responses import JSONResponse
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.boto import get_boto_client
from app.config.config_app import settings
from app.exceptions.responses import *
from app.models.model_files import FileEntity, Files
from app.models.model_users import RoleUser, Users
from app.schemas.schema_files import FileSchema
from app.utils.file_validation import validate_files
from app.services.service_base import ServiceBase



class ServiceFiles(ServiceBase):

    async def create(self, entity: FileEntity, entity_id: uuid.UUID, files: list[UploadFile], user: Users):
        try:
            # Валидация файлов перед загрузкой
            await validate_files(files)

            bucket = settings.MINIO_BUCKET
            files_orm = []
            async with get_boto_client() as s3:
                for file in files:
                    file_id = uuid.uuid4()
                    file_key = f"{file_id}/{file.filename}"
                    await s3.upload_fileobj(file.file, bucket, file_key)

                    file_orm = Files(
                        id=file_id,
                        user_id=user.id,
                        filename=file.filename,
                        original_size=file.size,
                        original_mime=file.content_type,
                    )
                    self.session.add(file_orm)
                    await self.session.execute(
                        insert(f"{entity.value}s_files")
                        .values({
                            "file_id":file_id,
                            f"{entity.value}_id": entity_id
                        }))
                    files_orm.append(file_orm)
                    
            await self.session.commit()
            return JSONResponse(
                content={'files': [FileSchema.model_validate(f).model_dump(mode="json") for f in files_orm]},
                status_code=201
            )

        except HTTPException:
            await self.session.rollback()
            raise
        
        except Exception as exc:
            logger.exception(exc)
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Internal Server Error")


    async def delete(self, file_id: uuid.UUID, user: Users):
        try:
            file = await self.session.get(Files, file_id)
            if file is None:
                raise ErrorNotExists(file_id, Files)
            
            if file.user_id != user.id and user.role is not RoleUser.admin:
                raise HTTPException(403, "This user have not permission for this operation")

            file_key = f"{file.id}/{file.filename}"
            async with get_boto_client() as s3:
                await s3.delete_object(
                    Bucket=file.bucket,
                    Key=file_key
                )

            await self.session.delete(file)
            await self.session.commit()
            return JSONResponse(
                {"status": "ok"},
                200
            )

        except HTTPException:
            await self.session.rollback()
            raise
        
        except Exception as exc:
            logger.exception(exc)
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Internal Server Error")

