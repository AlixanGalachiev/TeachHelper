from datetime import timedelta
from random import randint
from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import config_app
from app.models.model_user import User
from app.repositories.repo_user import UserRepo
from app.schemas.schema_auth import UserRead, UserRegister, UserResetPassword, UserToken

from app.utils.oAuth import create_access_token, get_current_user
from app.utils.password import verify_password, get_password_hash
from fastapi.security import OAuth2PasswordRequestForm
from app.services.service_mail import ServiceMail

class ServiceUser:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.mail = ServiceMail()

    async def validate_email(self, email: EmailStr):
        code = str(randint(0, 9999))
        await ServiceMail.send_mail_async(email, "Подтверждение почты", "template_verification_code.html", {"code": code})
        return {"message": "Код отправлен на почту"}

    async def register(self, user: UserRegister):
        repo = UserRepo(self.session)
        if await repo.email_exists(user.email):
            raise HTTPException(status.HTTP_409_CONFLICT, "User with this email already exists")

        user_db = User(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            password=get_password_hash(user.password),
            role=user.role,
		)

        db_user = await repo.create(user_db)
        await self.session.commit()
        return UserRead.model_validate(db_user)

    async def login(self, form_data: OAuth2PasswordRequestForm):
        repo = UserRepo(self.session)
        if not await repo.email_exists(form_data.username):
            raise HTTPException(status.HTTP_409_CONFLICT, "User with this email not exists")

        user = await repo.get_by_email(form_data.username)
        if not verify_password(form_data.password, user.password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect password")
        
        token = create_access_token({"email": form_data.username})
        return UserToken(token_type="Bearer", access_token=token)

    async def send_reset_mail(self, email: EmailStr):
        repo = UserRepo(self.session)
        if not await repo.email_exists(email):
            raise HTTPException(status.HTTP_409_CONFLICT, "User with this email not exists")
        
        user = await repo.get_by_email(email)
        
        token = create_access_token(email, timedelta.seconds(60))
        reset_link = f"{config_app.FRONT_URL}/reset-password?token={token}"
        await ServiceMail.send_mail_async(email, "Сброс пароля", "template_reset_password.html", {"name": user.first_name, "reset_link": reset_link})
        
        return {"message": "Письмо отправленно"}

    async def reset_password(self, data: UserResetPassword, user_data: User):
        user = await self.session.get(User, user_data.id)
        user.password = get_password_hash(data.password)
        await self.session.commit()
        return {"message": "Пароль обновлён"}
