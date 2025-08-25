from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import Optional, Literal

class UserRole(str, Enum):
    teacher = "teacher"
    student = "student"


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    middle_name: str | None = None
    last_name: str 
    role: UserRole


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    first_name: str
    middle_name: str | None = None
    last_name: str
    old_password: str
    new_password: str


class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True
