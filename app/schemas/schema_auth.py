from enum import Enum
import uuid
from pydantic import BaseModel, EmailStr

from app.models.model_users import RoleUser

class UserRegRole(str, Enum):
    teacher = "teacher"
    student = "student"

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

class UserResetPassword(BaseModel):
    password: str
    token: str

class UserRead(UserBase):
    id: uuid.UUID
    role: RoleUser
    is_verificated: bool
    
    model_config = {
        "from_attributes": True 
    }

class UserToken(BaseModel):
    token_type: str|None = None
    access_token: str|None = None
