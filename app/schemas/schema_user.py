from pydantic import BaseModel, EmailStr
from typing import Optional, Literal


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: Literal["teacher", "student"] = "student"


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[Literal["teacher", "student"]] = None


class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True
