from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str
    phone: str | None = None
    role_id: int | None = None


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    profile_image: str | None = None
    bio: str | None = None
    role_id: int | None = None
    is_active: bool | None = None


class UserResponse(UserBase):
    id: int
    phone: str | None = None
    profile_image: str | None = None
    bio: str | None = None
    role_id: int | None = None
    date_joined: datetime
    is_active: bool | None = True

    model_config = ConfigDict(from_attributes=True)