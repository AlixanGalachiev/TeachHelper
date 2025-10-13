from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.model_user import User
from app.repositories.repo_user import UserRepo
from app.settings import settings
from app.db import get_async_session
from app.schemas.schema_auth import UserRead



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
	to_encode = data.copy()
	expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
	to_encode.update({"exp": expire})
	return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_session)) -> User:
	repo = UserRepo(db)
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)
	try:
		payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
		email: str = payload.get("sub")
		if email is None:
			raise credentials_exception
	except JWTError:
		raise credentials_exception
	user = await repo.get_by_email(email=email)
	if user is None:
		raise credentials_exception
	return user
