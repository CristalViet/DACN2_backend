from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

from app.schemas.user_role import UserRoleResponse


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


class UserUpdatePatch(BaseModel):
    """
    PATCH update schema that accepts role as string (role name) instead of role_id.
    Used for frontend compatibility.
    """
    username: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    bio: str | None = None
    role: str | None = None  # Accept role name as string: "reader", "writer", "admin"
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

class UserWithRoleResponse(UserBase):
    id: int
    phone: str | None = None
    profile_image: str | None = None
    bio: str | None = None
    role_id: int | None = None
    role: Optional[UserRoleResponse] = None  
    date_joined: datetime
    is_active: bool | None = True

    model_config = ConfigDict(from_attributes=True)