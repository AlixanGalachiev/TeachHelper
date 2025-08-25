from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from app.db import get_async_session
from app.repositories.repo_user import UserRepo
from app.schemas.schema_user import UserCreate, UserRead
from app.utils.oAuth import create_access_token
from app.utils.password import verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserRead)
async def register(user: UserCreate, db: AsyncSession = Depends(get_async_session)):
	repo = UserRepo(db)
	existing_user = await repo.get_by_email(user.email)
	if existing_user:
		raise HTTPException(status_code=400, detail="Email already registered")
	result = await repo.create(user)
	await db.commit()
	return result

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_async_session)):
	repo = UserRepo(db)
	user = await repo.get_by_email(form_data.username)
	if not user or not verify_password(form_data.password, user.password_hash):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
	access_token = create_access_token(data={"sub": user.email})
	return {"access_token": access_token, "token_type": "bearer"}
