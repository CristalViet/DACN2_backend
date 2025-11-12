# 📄 🔟 app/schemas/user.py
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str
    full_name: str | None = None


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    full_name: str | None = None
    is_active: bool | None = None
    role_id: int | None = None


class UserResponse(UserBase):
    user_id: int
    full_name: str | None = None
    date_joined: datetime
    is_active: bool | None = True
    role_id: int | None = None

    model_config = ConfigDict(from_attributes=True)