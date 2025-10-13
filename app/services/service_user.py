from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.model_user import User
from app.repositories.repo_user import UserRepo
from app.schemas.schema_auth import UserForgotPassword, UserRead, UserRegister, UserResetPassword, UserToken

from app.utils.oAuth import create_access_token, get_current_user
from app.utils.password import verify_password, get_password_hash
from fastapi.security import OAuth2PasswordRequestForm
from app.services.service_mail import ServiceMail

class ServiceUser:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.mail = ServiceMail()

    async def register(self, user: UserRegister):
        repo = UserRepo(self.session)
        if await repo.email_exists(user.email):
            raise HTTPException(status.HTTP_409_CONFLICT, "User with this email already exists")

        user_db = User(
            first_name=user.first_name,
            second_name=user.second_name,
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
        
        token = create_access_token(form_data)
        
        return UserToken("Bearer", token)

    async def send_reset_mail(self, data: UserForgotPassword):
        repo = UserRepo(self.session)
        if not await repo.email_exists(data.email):
            raise HTTPException(status.HTTP_409_CONFLICT, "User with this email not exists")
        
        user = await repo.get_by_email(data.email)
        
        token = create_access_token(data.email, timedelta.seconds(60))
        await self.mail.send_reset_password(user.email, user.first_name, token)
        return {"message": "Письмо отправленно"}

    async def reset_password(self, data: UserResetPassword, user_data: User):
        user = await self.session.get(User, user_data.id)
        user.password = get_password_hash(data.password)
        await self.session.commit()
        return {"message": "Пароль обновлён"}
