from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import Optional, Literal

class UserRole(str, Enum):
    teacher = "teacher"
    student = "student"


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[Literal["teacher", "student"]] = None


class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True
