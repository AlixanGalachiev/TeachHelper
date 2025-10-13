from enum import Enum
import uuid
from pydantic import BaseModel, EmailStr
from typing import Optional, Literal

class UserRegRole(str, Enum):
    teacher = "teacher"
    student = "student"

class UserRole(str, Enum):
    teacher = "teacher"
    student = "student"
    admin = "admin"

class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr

class UserRegister(UserBase):
    password: str
    role: UserRegRole

    model_config = { 
        "json_schema_extra": {
            "example": {
                "first_name": "Иван",
                "last_name": "Иванов",
                "email": "ivan@example.com",
                "password": "123456",
                "role": "teacher"
            }
        }
    }


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    model_config = { 
        "json_schema_extra": {
            "example": {
                "email": "ivan@example.com",
                "password": "123456",
            }
        }
    }

class UserForgotPassword(BaseModel):
    email: EmailStr

class UserResetPassword(BaseModel):
    password: str

class UserRead(UserBase):
    id: uuid.UUID
    role: UserRole
    
    model_config = {
        "from_attributes": True 
    }

class UserToken(BaseModel):
    access_token: str|None = None
    token_type: str|None = None
