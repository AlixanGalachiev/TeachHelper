
import uuid
from fastapi import HTTPException, UploadFile, logger
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.config.boto import get_boto_client
from app.exceptions.exceptions import *
from app.models.model_users import RoleUser, Users
from tests.conftest import async_session


class ServiceFiles:
    def __init__(self, session: async_session):
        self.session = session


    async def create(self, bucket: str, files: list[UploadFile], user: Users):
        try:
            s3 = get_boto_client()
            files_orm = []
            for file in files:
                id = uuid.uuid4()
                await s3.upload_fileobj(file.file, bucket, f"{id}/{file.filename}")

                file_orm = Files(
                    id=id,
                    user_id=user.id,
                    filename=file.filename,
                    bucket=bucket,
                    original_size=file.size,
                    original_mime=file.content_type,
                )
                self.session.add(file_orm)
                files_orm.append(file_orm)
                    
            await self.session.commit()
            return JSONResponse(
                content={'files': [FileRead.model_validate(f).model_dump(mode="json") for f in files_orm]},
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

            s3 = get_boto_client()
            await s3.delete_object(
                bucket=file.bucket,
                Key=file.s3_key
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

