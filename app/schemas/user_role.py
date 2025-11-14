from pydantic import BaseModel, ConfigDict


class UserRoleCreate(BaseModel):
    role_name: str
    permissions: str | None = None


class UserRoleUpdate(BaseModel):
    role_name: str | None = None
    permissions: str | None = None


class UserRoleResponse(BaseModel):
    id: int
    role_name: str
    permissions: str | None = None

    model_config = ConfigDict(from_attributes=True)


