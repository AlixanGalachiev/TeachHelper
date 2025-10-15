from datetime import timedelta
from random import randint
from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.config_app import settings
from app.models.model_users import Users
from app.repositories.repo_user import UserRepo
from app.schemas.schema_auth import UserRead, UserRegister, UserResetPassword, UserToken

from app.utils.oAuth import create_access_token, get_current_user
from app.utils.password import verify_password, get_password_hash
from fastapi.security import OAuth2PasswordRequestForm
from app.services.service_mail import ServiceMail

from jose import jwt

class ServiceUser:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.mail = ServiceMail()


    async def register(self, user: UserRegister):
        repo = UserRepo(self.session)
        if await repo.email_exists(user.email):
            raise HTTPException(status.HTTP_409_CONFLICT, "User with this email already exists")

        user_db = Users(
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

        if not user.is_verificated:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Please confirm your email first")
        
        token = create_access_token({"email": form_data.username})
        return UserToken(token_type="Bearer", access_token=token)


    async def send_email_confirmation_link(self, email: EmailStr):
        repo = UserRepo(self.session)
        if not await repo.email_exists(email):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User with this email not exists")

        user = await repo.get_by_email(email)
        if user.is_verificated:
            raise HTTPException(status.HTTP_409_CONFLICT, detail="User is already verificated")

        token = create_access_token(email, timedelta(seconds=60))
        verify_link = f"{settings.FRONT_URL}/confirm_email?token={token}"
        await ServiceMail.send_mail_async(email, "Подтверждение почты", "template_verification_code.html", {"verify_link": verify_link})

        return {"message": "Письмо отправленно"}


    async def confirm_email(self, token: str):
        if not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token format")

        jwt_token = token.split("Bearer ")[1]
        payload = jwt.decode(jwt_token, settings.SECRET_CONFIRM_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token")

        user = await self.session.get(UserRegister, {"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.is_verificated = True
        await self.session.commit()
        return {"message": "Почта подтверждена"}


    async def forgot_password(self, email: EmailStr):
        repo = UserRepo(self.session)
        if not await repo.email_exists(email):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User with this email not exists")

        user = await repo.get_by_email(email)
        if not user.is_verificated:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Please confirm your email first")

        token = create_access_token(email, timedelta(seconds=60))
        reset_link = f"{settings.FRONT_URL}/reset_password?token={token}"
        await ServiceMail.send_mail_async(email, "Сброс пароля", "template_verification_code.html", {"name": user.first_name, "reset_link": reset_link})

        return {"message": "Письмо отправлено"}
    
    async def reset_password(self, reset_data: UserResetPassword):
        if not reset_data.token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token format")

        jwt_token = reset_data.token.split("Bearer ")[1]
        payload = jwt.decode(jwt_token, settings.SECRET_RESET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token")

        user = await self.session.get(UserRegister, {"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.password = get_password_hash(reset_data.password)
        self.session.commit()
        return {"message": "Пароль обновлён"}
