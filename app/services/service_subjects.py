import uuid

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.model_subjects import Subjects
from app.models.model_users import RoleUser, Users
from app.schemas.schema_subjects import SubjectRead
from app.utils.logger import logger
from app.services.service_base import ServiceBase

class ServiceSubjects(ServiceBase):

    async def create(self, name: str, user: Users):
        try:
            if user.role is not RoleUser.admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="This user can't create new subjects"
                )

            subject = Subjects(name=name)
            self.session.add(subject)
            await self.session.commit()
            return JSONResponse(content={"status": "ok"})

        except HTTPException as exc:
            raise 

        except Exception as exc:
            logger.exception(exc)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def get_all(self) -> list[SubjectRead]:
        try:
            stmt = (select(
                Subjects.id,
                Subjects.name
                ))
            result = await self.session.execute(stmt)
            return [SubjectRead.model_validate(row) for row in result.mappings().all()]

        except HTTPException as exc:
            raise
        
        except Exception as exc:
            logger.exception(exc)
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Internal Server Error")


    async def patch(self, id: uuid.UUID, user: Users):
        try:
            if user.role is not RoleUser.admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="This user can't create new subjects"
                )

            subject = await self.session.get(Subjects, id)
            if subject is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This subject not exists")

            return JSONResponse(content={"status": "ok"})
        except HTTPException as exc:
            raise
        
        except Exception as exc:
            logger.exception(exc)
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Internal Server Error")

    async def delete(self, id: uuid.UUID, user: Users):
        try:
            if user.role is not RoleUser.admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="This user can't create new subjects"
                )

            subject = await self.session.get(Subjects, id)
            if subject is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This subject not exists")
            
            await self.session.delete(subject)
            await self.session.commit()
            return JSONResponse(content={"status": "ok"})

        except HTTPException as exc:
            raise
        
        except Exception as exc:
            logger.exception(exc)
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Internal Server Error")

