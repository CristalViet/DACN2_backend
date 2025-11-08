from pydantic import BaseModel, ConfigDict


class UserRoleCreate(BaseModel):
    name: str


class UserRoleUpdate(BaseModel):
    name: str | None = None


class UserRoleResponse(BaseModel):
    role_id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


