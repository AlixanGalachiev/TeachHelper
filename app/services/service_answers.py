import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.exceptions.responses import ErrorNotExists, ErrorPermissionDenied, ErrorRolePermissionDenied, Success
from app.models.model_users import RoleUser, Users
from app.models.model_works import Answers, Works
from app.schemas.schema_work import AnswerUpdate
from app.services.service_base import ServiceBase
from app.utils.logger import logger

class ServiceAnswers(ServiceBase):

    async def update_comment(
        self,
        work_id: uuid.UUID,
        id: uuid.UUID,
        general_comment: str,
        user: Users
    ):
        try:
            work_db = await self.session.get(
                Works, work_id, options={"Works.task"}
            )

            if work_db is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work not found")

            if work_db.task.id != user.id:
                raise ErrorPermissionDenied()

            answer_db = await self.session.get(Answers, id)
            if answer_db is None: 
                raise ErrorNotExists()

            answer_db.general_comment = general_comment
            await self.session.commit()

            return Success

        except HTTPException:
            await self.session.rollback()
            raise

        except Exception as exc:
            logger.exception(exc)
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Internal Server Error")
        
# 2 запроса для учителей и для учеников
# сделать на фронте
# проверять роль и в зависимости от неё менять files, если учитель то не изменять, а если ученик делать это с комментариями и критериями

# Проблема в том, что нужно для каждой сущности написать запросы 
# на их обновление, а потом эти данные получить

# Нужно написать запросы на patch Answers, ACriterions, Files, Comments

# Чтобы обновить answers добавляем или удаляем api/files


# Answers - изменяется только учеником, нужно создать файл и привязать его к ответу
# ACriterions - изменяется только учителем, нужно изменить критерий и потом получить 
#     данные
# Comments - изменяется учителем у них есть файлы  

# На файлы делать отдельный crud, чтобы привязать их к отдельной сущности надо, СДЕЛАЛ ФАЙЛЫ
#     либо обновить сущность передав в неё файл, либо написать отдельные запросы
#     entity/{id}/files и вместо entity писать разные сущности. Минус придётся 
#     дублировать код. Или можно передавать название сущности и привязывать файл
#     к определённой таблице. 

# Сначала создается Задание у него создаются упражнения, потом задание рассылается
# в этот момент создаются работы, ответы.
# Теперь ученик может изменять ответы в работе и изменять статус работы
# После отправки работы на проверку учитель может работать с комментариями
# и указывать каким критериям работа соответствует изменять статус работы.

# Разделить api на учеников и учителей, нужно если они могут изменять один и тот же объект
    # но только свою часть.