from fastapi import APIRouter, Depends
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from app.db import get_async_session
from app.models.model_users import Users
from app.schemas.schema_auth import UserRegister, UserRead, UserToken, UserResetPassword
from app.services.service_auth import ServiceAuth
from app.utils.oAuth import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserRead)
async def register(user: UserRegister, session: AsyncSession = Depends(get_async_session)):
    service = ServiceAuth(session)
    return await service.register(user)

@router.post("/login", response_model=UserToken)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_async_session)):
    service = ServiceAuth(session)
    return await service.login(form_data)

@router.post("/send_email_confirmation_link")
async def send_email_confirmation_link(email: EmailStr, session: AsyncSession = Depends(get_async_session)):
    service = ServiceAuth(session)
    return await service.send_email_confirmation_link(email)

@router.post("/confirm_email")
async def confirm_email(token: str, session: AsyncSession = Depends(get_async_session)):
    service = ServiceAuth(session)
    return await service.confirm_email(token)   

@router.post("/forgot_password")
async def forgot_password(email: EmailStr, session: AsyncSession = Depends(get_async_session)):
    service = ServiceAuth(session)
    return await service.forgot_password(email)

@router.post("/reset_password")
async def reset_password(reset_data: UserResetPassword, session: AsyncSession = Depends(get_async_session)):
    service = ServiceAuth(session)
    return await service.reset_password(reset_data=reset_data)

@router.get("/me", response_model=UserRead)
async def me(current_user: Users = Depends(get_current_user)):
    return UserRead.model_validate(current_user)
