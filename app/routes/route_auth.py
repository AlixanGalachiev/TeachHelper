from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from app.db import get_async_session
from app.models.model_user import User
from app.repositories.repo_user import UserRepo
from app.schemas.schema_auth import UserRegister, UserForgotPassword, UserRead, UserReadWithToken, UserResetPassword
from app.services.service_user import ServiceUser
from app.utils.oAuth import create_access_token, get_current_user
from app.utils.password import verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserRead)
async def register(user: UserRegister, session: AsyncSession = Depends(get_async_session)):
    service = ServiceUser(session)
    return await service.register(user)

@router.post("/login", response_model=UserReadWithToken)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_async_session)):
    service = ServiceUser(session)
    return await service.login(form_data)

@router.post("/forgot_password")
async def forgot_password(data: UserForgotPassword, session: AsyncSession = Depends(get_async_session)):
    service = ServiceUser(session)
    return await service.send_reset_mail(data)

@router.post("/reset_password")
async def reset_password(data: UserResetPassword, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    service = ServiceUser(session)
    return await service.reset_password(data)

@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)):
    return UserRead.model_validate(current_user)
